"""
Implements some reusable functionality for experimentation.
"""

import datetime
import os
from subprocess import Popen
from time import sleep
import json
from os import getenv
from dataclasses import dataclass
from argparse import Namespace
import math

import dotenv

import gssi_experiment.util.util as util
from gssi_experiment.util.prometheus_helper import (
    LatestCpuUtilizationFetcher,
    TIME_FORMAT,
)
import gssi_experiment.util.mubench_helper as mubench_helper

dotenv.load_dotenv()


@dataclass(frozen=True)
class ExperimentParameters:
    k8s_parameters_path: str
    runner_parameter_path: str
    yaml_builder_path: str
    output_folder: str
    pod_initialize_delay: int = 10
    prometheus_fetch_delay: int = 30


def run_experiment(args: Namespace, exp_params: ExperimentParameters):
    if not os.path.exists(exp_params.output_folder):
        os.makedirs(exp_params.output_folder)

    # Runs experiment
    start_time = datetime.datetime.now()
    _run_experiment(
        exp_params.k8s_parameters_path,
        exp_params.runner_parameter_path,
        exp_params.yaml_builder_path,
        exp_params.pod_initialize_delay,
    )
    end_time = datetime.datetime.now()

    sleep(1)
    _write_metadata(exp_params.output_folder, start_time, end_time, exp_params, args)
    _write_mubench_data(exp_params.output_folder)

    print(f"Waiting {exp_params.prometheus_fetch_delay}s to fetching Prometheus data.")
    sleep(exp_params.prometheus_fetch_delay)
    delta_time = (end_time - start_time).seconds
    data_time_window = math.ceil((delta_time + exp_params.prometheus_fetch_delay) / 60)
    _write_prometheus_data(exp_params.output_folder, data_time_window, start_time)


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
            "--clean-deployment",
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


def _write_mubench_data(output_folder):
    mubench_results_path = "./SimulationWorkspace/Result/result.txt"
    mubench_output_path = f"{output_folder}/mubench_results.csv"
    mubench_helper.rewrite_mubench_results(mubench_results_path, mubench_output_path)


def _write_prometheus_data(
    output_folder, data_time_window: int, start_time: datetime.datetime
):
    # Fetches CPU utilization.
    cpu_utilization_output_path = f"{output_folder}/cpu_utilization_raw.csv"
    time_window_padding = 5
    time_window_in_minutes = data_time_window + time_window_padding
    print(f"Collecting data in most recent window of {time_window_in_minutes} minutes.")
    fetcher = LatestCpuUtilizationFetcher(
        cpu_utilization_output_path, time_window_in_minutes, start_time
    )
    fetcher.fetch_latest_cpu_utilization()


def _write_metadata(
    output_folder,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    exp_params: ExperimentParameters,
    args: Namespace,
):
    # Write meta data file
    meta_data = {
        "start_time": start_time.strftime(TIME_FORMAT),
        "end_time": end_time.strftime(TIME_FORMAT),
        "experiment_parameters": exp_params.__dict__,
        "cmd_arguments": args.__dict__,
        "experiment_files": {
            "k8s_parameters": util.load_json(exp_params.k8s_parameters_path),
            "runner_parameters": util.load_json(exp_params.runner_parameter_path),
        },
    }
    meta_data["experiment_files"]["work_model"] = util.load_json(
        meta_data["experiment_files"]["k8s_parameters"]["WorkModelPath"]
    )
    with open(
        f"{output_folder}/metadata.json", "w+", encoding="utf-8"
    ) as metadata_output_file:
        metadata_output_file.write(json.dumps(meta_data, indent=4))


def get_output_folder(
    base_folder: str, name: str, step_idx: "int | None" = None
) -> str:
    """Returns a folder name."""
    today = datetime.datetime.now()
    today = today.strftime("%Y_%m_%d")
    if step_idx is None:
        path = f"{base_folder}/results/{name}/{today}/"
    else:
        path = f"{base_folder}/results/{name}/{today}/{step_idx}_steps/"
    path = os.path.abspath(path)
    return path


def get_server_endpoint() -> str:
    """Retrieves server endpoint from the environment."""
    key = "SERVER_API_ENDPOINT"
    server_endpoint = getenv(key)
    if server_endpoint is None:
        raise ValueError(f'Environment variable "{key}" is not set.')
    print(f'Retrieved server endpoint: "{server_endpoint}".')
    return server_endpoint
