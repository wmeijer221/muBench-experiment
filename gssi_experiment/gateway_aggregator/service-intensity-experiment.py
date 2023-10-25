"""Runs service intensity experiment and outputs results."""

import argparse
from os import remove
from subprocess import Popen
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np


def create_worker_params(experiment_idx: int):
    """1: prepares the experiment."""
    step_size = 1.0 / args.simulation_steps
    s1_intensity = experiment_idx * step_size

    experiment_params = BASE_WORKER_PARAM.format(
        s1_intensity=s1_intensity, s3_intensity=1 - s1_intensity
    )

    with open(
        args.temp_worker_param_path, mode="w+", encoding="utf-8"
    ) as temp_work_params:
        print(
            f"experiment-{experiment_idx + 1}/{args.simulation_steps + 1}: {s1_intensity=}, {temp_work_params.name=}"
        )
        temp_work_params.write(experiment_params)
        print(experiment_params)


def run_experiment():
    """2: runs the experiment."""
    popen_args = [
        "./gssi_experiment/run-full-experiment.sh",
        "./gssi_experiment/gateway_aggregator/K8sParameters.json",
        args.temp_worker_param_path,
    ]
    print(popen_args)
    proc = Popen(popen_args)
    proc.wait()


def calculate_results(experiment_idx: int) -> Tuple:
    """3: processes the results."""

    step_size = 1.0 / args.simulation_steps
    s1_intensity = experiment_idx * step_size

    with open(
        "./SimulationWorkspace/Result/result.txt", "r", encoding="utf-8"
    ) as results_file:
        delays = []
        for entry in results_file:
            elements = entry.split()
            delay = int(elements[1])
            delays.append(delay)
        mn = np.min(delays)
        mx = np.max(delays)
        avg = np.average(delays)
        std = np.std(delays)

        print(f"{s1_intensity=}: {mn=}, {mx=}, {avg=}, {std=}")
        results = (s1_intensity, mn, mx, avg, std)
        return results


def visualize_results(experimental_results: List[Tuple]):
    # Dummy data
    # experimental_results = [
    #     (0.4, 63, 1129, 312.7676,143.06962078037392),
    #     (0.6, 63, 1045, 295.2754, 133.2716202154082),
    #     (0.8, 57,  1132,  296.3602, 140.70607256248752)
    # ]

    print(experimental_results)

    # 4: plots the results
    x = [point[0] for point in experimental_results]
    y_min = [point[1] for point in experimental_results]
    y_max = [point[2] for point in experimental_results]
    y_avg = [point[3] for point in experimental_results]
    std_dev = [point[4] for point in experimental_results]

    # Creating the line chart
    plt.figure(figsize=(10, 6))
    plt.plot(x, y_min, label="Min")
    plt.plot(x, y_max, label="Max")
    plt.plot(x, y_avg, label="Average")

    # Creating the area around the average line for the standard deviation
    plt.fill_between(
        x,
        np.subtract(y_avg, std_dev),
        np.add(y_avg, std_dev),
        color="b",
        alpha=0.2,
        label="Standard Deviation",
    )

    # Adding labels and title
    plt.xlabel("S1 Intensity")
    plt.ylabel("Delay (ms)")
    plt.title("Differences in delay for different values of S1 Intensity.")
    plt.legend()
    plt.grid(True)
    # plt.show()
    plt.savefig("./gssi_experiment/gateway_aggregator/figure.png")


def main():
    """Runs complete experiment."""
    experimental_results = []

    for i in range(args.simulation_steps + 1):
        create_worker_params(i)
        run_experiment()
        results = calculate_results(i)
        experimental_results.append(results)

    visualize_results(experimental_results)

    # 5: cleanup
    remove(args.temp_worker_param_path)


parser = argparse.ArgumentParser()
parser.add_argument(
    "-p",
    "--tmp-worker-param-path",
    action="store",
    dest="temp_worker_param_path",
    default="./gssi_experiment/gateway_aggregator/tmp_work_model.json",
    help="File path where the experiments' work models are temporarily stored.",
)
parser.add_argument(
    "-s",
    "--steps",
    type=int,
    action="store",
    dest="simulation_steps",
    default=5,
    help="The number of simulations that are performed w.r.t. S1 intensity.",
)

args = parser.parse_args()

BASE_WORKER_PARAM = """{{
   "RunnerParameters": {{
      "ms_access_gateway": "http://192.168.49.2:31113",
      "workload_files_path_list": [
         "SimulationWorkspace/workload.json"
      ],
      "workload_rounds": 1,
      "workload_type": "greedy",
      "workload_events": 4000,
      "thread_pool_size": 8,
      "result_file": "result",
      "ingress_service": "mubench-ingress",
      "HeaderParameters": [
            {{
                "type": "RequestTypeHeader",
                "parameters": {{
                    "request_types": [
                        "s1_intensive",
                        "s3_intensive"
                    ],
                    "probabilities": [
                        {s1_intensity},
                        {s3_intensity}
                    ]
                }}
            }},
            {{
                "type": "StaticHeaderFactory",
                "parameters": {{
                    "x-baseendpoint": "http://192.168.49.2:31113/",
                    "x-aggregatedendpoints": "s1,s2,s3"
                }}
            }}
        ]
   }},
   "OutputPath": "SimulationWorkspace/Result",
   "_AfterWorkloadFunction": {{
      "_comment": "remove _ from the object name to execute the funcions",
      "file_path": "Function",
      "function_name": "get_prometheus_stats"
   }}
}}"""

# BASE_WORKER_PARAM = """{{
#    "RunnerParameters": {{
#       "ms_access_gateway": "http://192.168.49.2:31113",
#       "workload_files_path_list": [
#          "SimulationWorkspace/workload.json"
#       ],
#       "workload_rounds": 1,
#       "workload_type": "greedy",
#       "workload_events": 400,
#       "thread_pool_size": 14,
#       "result_file": "result",
#       "ingress_service": "mubench-ingress",
#       "HeaderParameters": [{{
#          "type": "AggregatedHeaderFactory",
#          "parameters": {{
#             "base_endpoint": "http://192.168.49.2:31113/",
#             "endpoints": [
#                "s1",
#                "s2",
#                "s3"
#             ],
#             "probabilities": [
#                {s1_intensity},
#                1,
#                {s3_intensity}
#             ]
#          }}
#       }}
#    }},
#    "OutputPath": "SimulationWorkspace/Result",
#    "_AfterWorkloadFunction": {{
#       "_comment": "remove _ from the object name to execute the funcions",
#       "file_path": "Function",
#       "function_name": "get_prometheus_stats"
#    }}
# }}
# """

main()
