"""
Runs service intensity experiment and outputs results.
"""

from datetime import datetime
import math
import os
from typing import Tuple

import requests
from requests.auth import HTTPBasicAuth
import dotenv
import pandas as pd

import gssi_experiment.util.args_helper as args_helper
import gssi_experiment.util.doc_helper as doc_helper
import gssi_experiment.util.experiment_helper as exp_helper
import gssi_experiment.util.node_selector_helper as ns_helper
import gssi_experiment.util.prometheus_helper as prom_helper
import gssi_experiment.util.prometheus_raw_data_helper as prom_data_helper
import gssi_experiment.util.tmp_exp_doc_helper as tmp_doc_helper
import gssi_experiment.util.util as util
import gssi_experiment.util.notebook_helper as nb_helper

dotenv.load_dotenv()

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
print(f"{BASE_FOLDER=}")

parser = args_helper.init_args(BASE_FOLDER)
args = parser.parse_args()
args.simulation_steps = max(args.simulation_steps, 1)

SERVICE_NAME = "s1"


def write_tmp_work_model(work_model_path: str, range_complexity: int) -> str:
    tmp_work_model_path = f"{work_model_path}.tmp"
    doc_helper.write_concrete_data_document(
        work_model_path,
        tmp_work_model_path,
        overwritten_fields=[
            (
                [
                    SERVICE_NAME,
                    "internal_service",
                    "loader",
                    "cpu_stress",
                    "range_complexity",
                ],
                [range_complexity, range_complexity],
            )
        ],
        editor_type=doc_helper.JsonEditor,
    )
    return tmp_work_model_path


def request_performance_results(start_time: datetime, output_folder: str) -> str:
    prom_user = os.getenv("PROM_USER")
    prom_pass = os.getenv("PROM_PASS")
    target_endpoint = os.getenv("PROMETHEUS_API_ENDPOINT")

    time_window_in_minutes = math.ceil((datetime.now() - start_time).seconds / 60) + 1

    endpoint = f"{target_endpoint}/api/v1/query"
    url_params = {
        # "query": f"mub_internal_processing_latency_seconds_sum[{time_window_in_minutes}m]",
        "query": f"mub_request_processing_latency_seconds_sum[{time_window_in_minutes}m]",
    }

    auth = HTTPBasicAuth(prom_user, prom_pass)
    response = requests.get(endpoint, params=url_params, auth=auth)
    print(f"Prometheus response status: {response.status_code}")

    output_path = f"{output_folder}/service_delay.csv"
    tmp_output_path = f"{output_path}.tmp"
    with open(tmp_output_path, "w+", encoding="utf-8") as output_file:
        output_file.write(response.text)

    fetcher = prom_helper.LatestCpuUtilizationFetcher(
        output_path, time_window_in_minutes, start_time
    )
    fetcher.fetch_latest_cpu_utilization(fetch_new_data=False)

    return output_path


def improve_workload_estimation(work_model_path: str, service_delay_path: str) -> Tuple[int, int]:
    # Calculates averages.
    df = pd.read_csv(service_delay_path, header=0)
    nb_helper.reset_column_name_indices(df)
    my_services = [col for col in df.columns if col.startswith(SERVICE_NAME)]
    averages = prom_data_helper.calculate_average_cpu_time_from_df(df, my_services)
    print(f"{len(averages)=}")
    average_delay = averages[0] * 1000
    print(f"{average_delay=:.3f}")

    # Calculates current complexity and expected service load.
    work_model = util.load_json(work_model_path)
    curr_complexity = work_model[SERVICE_NAME]["internal_service"]["loader"][
        "cpu_stress"
    ]["range_complexity"]
    curr_complexity = math.floor(sum(curr_complexity) / len(curr_complexity))
    target_delay = work_model[SERVICE_NAME]["internal_service"]["loader"][
        "cpu_stress"
    ]["trials"]

    # Updates complexity according to mismatch in results.
    mismatch_ratio = target_delay / average_delay
    new_complexity = math.ceil(curr_complexity * mismatch_ratio)
    print(
        f"{new_complexity=} ({target_delay} / {average_delay:.2f} * {curr_complexity} = {new_complexity})"
    )
    return new_complexity, mismatch_ratio


def run_the_experiment():
    """Does what it says."""

    mubench_k8s_template_folder = os.path.dirname(BASE_FOLDER)

    # Overwrites affinity in GA service and muBench service yamls.
    ns_helper.load_and_write_node_affinity_template(args, mubench_k8s_template_folder)
    k8s_param_path = os.path.dirname(__file__) + "/K8sParameters.json"
    k8s_params_file_path = f"{k8s_param_path}.tmp"
    tmp_doc_helper.write_tmp_k8s_params(
        k8s_param_path, k8s_params_file_path, args.cpu_limit, args.replicas
    )

    # Calculates the standard complexity.
    work_model_path = f"{BASE_FOLDER}/WorkModel.json"
    work_model = util.load_json(work_model_path)
    curr_complexity = work_model[SERVICE_NAME]["internal_service"]["loader"][
        "cpu_stress"
    ]["range_complexity"]
    curr_complexity = math.floor(sum(curr_complexity) / len(curr_complexity))

    tested_complexities = [(curr_complexity, 0)]

    for step_idx in range(args.simulation_steps):
        # Executes experiments for every considered s1 intensity value.
        tmp_runner_param_file_path = tmp_doc_helper.overwrite_access_gateway(
            args.base_runner_param_file_name
        )
        tmp_work_model_path = write_tmp_work_model(work_model_path, curr_complexity)

        output_folder = exp_helper.get_output_folder(BASE_FOLDER, args.name, step_idx)
        exp_params = exp_helper.ExperimentParameters(
            k8s_params_file_path,
            tmp_runner_param_file_path,
            mubench_k8s_template_folder,
            output_folder,
            args.wait_for_pods_delay,
        )

        start_time = datetime.now()
        exp_helper.run_experiment(args, exp_params)
        output_path = request_performance_results(start_time, output_folder)
        curr_complexity, mismatch_ratio = improve_workload_estimation(tmp_work_model_path, output_path)
        tested_complexities.append((curr_complexity, mismatch_ratio))

    print(f"{tested_complexities}")


if __name__ == "__main__":
    run_the_experiment()
