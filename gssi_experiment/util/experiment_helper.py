"""
Implements some reusable functionality for experimentation.
"""

import csv
import datetime
import os
from subprocess import Popen
from typing import Dict, Tuple, Generator
from time import sleep
import itertools
import json

import numpy as np

import gssi_experiment.util.doc_helper as doc_helper
from gssi_experiment.util.prometheus_helper import (
    fetch_service_cpu_utilization,
    TIME_FORMAT,
)


def write_tmp_service_params_for_node_selector(
    aggregator_service_path: str,
    tmp_aggregator_service_path: str,
    target_node: "str | None",
) -> str:
    """Sets the target node field inside the deployment yaml and outputs it to a temp file."""
    if target_node is None:
        return aggregator_service_path
    doc_helper.write_concrete_data_document(
        aggregator_service_path,
        tmp_aggregator_service_path,
        overwritten_fields=[
            (
                # NOTE: Assumes the Deployment entity has index 3.
                [3, "spec", "template", "spec", "nodeSelector"],
                {"kubernetes.io/hostname": target_node},
            )
        ],
        editor_type=doc_helper.YamlEditor,
    )
    return tmp_aggregator_service_path


def write_tmp_work_model_for_trials(
    base_worker_model_file_name: str, tmp_base_worker_model_file_path: str, trials: int
) -> None:
    """Overwrites the trials field in the WorkModel json file and outputs it to a tmp file."""
    base_path = [
        "__service",  # is overwritten
        "internal_service",
        "__request_type",  # is overwritten
        "loader",
        "cpu_stress",
        "trials",
    ]
    services = ["s1", "s2", "s3"]
    request_types = ["s1_intensive", "s3_intensive"]

    def nested_key_generator() -> Generator:
        for service, request_type in itertools.product(services, request_types):
            base_path[0] = service
            base_path[2] = request_type
            yield (base_path, trials)

    doc_helper.write_concrete_data_document(
        base_worker_model_file_name,
        tmp_base_worker_model_file_path,
        overwritten_fields=nested_key_generator(),
        editor_type=doc_helper.JsonEditor,
    )


def run_experiment2(
    k8s_parameters_path: str,
    runner_parameter_path: str,
    yaml_builder_path: str,
    output_folder: str,
    pod_initialize_delay: int = 10,
    prometheus_fetch_delay: int = 30,
):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Runs experiment
    start_time = datetime.datetime.now()
    _run_experiment(
        k8s_parameters_path,
        runner_parameter_path,
        yaml_builder_path,
        pod_initialize_delay,
    )
    end_time = datetime.datetime.now()
    sleep(1)
    mubench_results_path = "./SimulationWorkspace/Result/result.txt"
    mubench_output_path = f"{output_folder}/mubench_results.csv"
    _rewrite_mubench_results(mubench_results_path, mubench_output_path)

    # Fetches CPU utilization.
    cpu_utilization_output_path = f"{output_folder}/cpu_utilization.csv"
    fetch_start = start_time - datetime.timedelta(minutes=2)
    fetch_end = end_time + datetime.timedelta(minutes=2)
    print(f"Waiting {prometheus_fetch_delay} seconds before fetching Prometheus data.")
    sleep(prometheus_fetch_delay)
    fetch_service_cpu_utilization(cpu_utilization_output_path, fetch_start, fetch_end)

    # Write meta data file
    meta_data = {
        "start_time": start_time.strftime(TIME_FORMAT),
        "end_time": end_time.strftime(TIME_FORMAT),
        "muBench_results_path": mubench_output_path,
        "Prometheus_cpu_utilization_path": cpu_utilization_output_path,
    }
    with open(
        f"{output_folder}/metadata.json", "w+", encoding="utf-8"
    ) as metadata_output_file:
        metadata_output_file.write(json.dumps(meta_data, indent=4))


def _run_experiment(
    k8s_parameters_path: str,
    runner_parameter_path: str,
    yaml_builder_path: str,
    pod_initialize_delay: int = 10,
):
    """Experiment runner that does not depend on a bash script."""
    current_proc: Popen = None
    try:
        # 1: Deploy topology:
        args = [
            "python3",
            "./Deployers/K8sDeployer/RunK8sDeployer.py",
            "-c",
            k8s_parameters_path,
            "-y",
            "-r",
            "-ybp",
            yaml_builder_path,
        ]
        current_proc = Popen(args)
        current_proc.wait()

        # 2: Wait for deployment to complete.
        print(f"Waiting {pod_initialize_delay} seconds for pods to start.")
        sleep(pod_initialize_delay)

        # 3: run experiment
        args = ["python3", "./Benchmarks/Runner/Runner.py", "-c", runner_parameter_path]
        current_proc = Popen(args)
        current_proc.wait()
    except KeyboardInterrupt:
        if current_proc:
            current_proc.terminate()
        raise


def _rewrite_mubench_results(input_path: str, output_path: str):
    with open(output_path, "w+", encoding="utf-8") as output_file:
        csv_writer = csv.writer(output_file)
        headers = [
            "timestamp",
            "latency_ms",
            "status_code",
            "processed_requests",
            "pending_requests",
        ]
        with open(input_path, "r", encoding="utf-8") as input_file:
            for i, line in enumerate(input_file):
                chunks = line.split()
                msg_headers = [ele[1:-1].split(":") for ele in chunks[5:]]
                if i == 0:
                    header_keys = [ele[0][2:] for ele in msg_headers]
                    headers = [*headers, *header_keys]
                    csv_writer.writerow(headers)
                msg_headers = [":".join(ele[1:]) for ele in msg_headers]
                data_point = [*chunks[:5], *msg_headers]
                csv_writer.writerow(data_point)


def apply_k8s_yaml_file(file_path: str):
    """Applies a yaml field using kubectl"""
    args = ["kubectl", "apply", "-f", file_path]
    proc = Popen(args)
    statuscode = proc.wait()
    if statuscode != 0:
        raise ValueError(f'Could not apply "{file_path}".')


def restart_deployment(deployment_name: str):
    """Rolls out a restart for th egiven deployment."""
    args = ["kubectl", "rollout", "restart", "deployment", deployment_name]
    Popen(args).wait()


def calculate_basic_statistics(
    experiment_idx: int,
    simulation_steps: int,
    result_file_path: str = "./SimulationWorkspace/Result/result.txt",
) -> Dict[str, Tuple]:
    """
    Calculates the min, max, mean, std of each variable.
    Generates separate results for messages with different
    ``x-requesttype`` header fields.
    """

    step_size = 1.0 / simulation_steps
    s1_intensity = experiment_idx * step_size

    all_data_key = "all"

    with open(result_file_path, "r", encoding="utf-8") as results_file:
        delays_per_group = {all_data_key: []}
        delays = []
        for entry in results_file:
            elements = entry.split()
            delay = int(elements[1])
            delays_per_group[all_data_key].append(delay)
            # splits by message type
            message_type = list(
                [ele for ele in elements if ele.startswith('"x-requesttype:')]
            )[0]
            message_type = message_type[1:-1].split(":")[1]
            if message_type not in delays_per_group:
                delays_per_group[message_type] = []
            delays_per_group[message_type].append(delay)
        # Calculates basic statistics.
        results = {}
        for key, delays in delays_per_group.items():
            mn = np.min(delays)
            mx = np.max(delays)
            avg = np.average(delays)
            std = np.std(delays)
            results[key] = (s1_intensity, mn, mx, avg, std)
            print(f"{s1_intensity=}, {key=}: {mn=}, {mx=}, {avg=}, {std=}")
        return results
