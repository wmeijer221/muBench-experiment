"""Runs service intensity experiment and outputs results."""

import argparse
from os import remove
from subprocess import Popen
from typing import List, Tuple
from copy import deepcopy
import json
import matplotlib.pyplot as plt
import numpy as np


def create_worker_params(experiment_idx: int, base_worker_param: dict):
    """1: prepares the experiment."""
    step_size = 1.0 / args.simulation_steps
    s1_intensity = experiment_idx * step_size

    experiment_params = deepcopy(base_worker_param)
    experiment_params["RunnerParameters"]["HeaderParameters"][0]["parameters"][
        "probabilities"
    ] = [s1_intensity, 1 - s1_intensity]

    with open(
        args.temp_worker_param_path, mode="w+", encoding="utf-8"
    ) as temp_work_params:
        print(
            f"experiment-{experiment_idx + 1}/{args.simulation_steps + 1}: {s1_intensity=}, {temp_work_params.name=}"
        )
        temp_work_params.write(json.dumps(experiment_params, indent=4))
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
    """Generates line diagrams with the results."""
    # Dummy data
    # experimental_results = [
    #     (0.0, 1032, 5194, 2403.3975, 1008.6441317401049),
    #     (0.3333333333333333, 404, 3827, 1571.87, 669.5256067545139),
    #     (0.6666666666666666, 604, 7421, 1900.1825, 1004.7100995778583),
    #     (1.0, 787, 4137, 1875.055, 623.988887701536),
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


def main(base_worker_param: dict):
    """Runs complete experiment."""
    experimental_results = []

    for i in range(args.simulation_steps + 1):
        create_worker_params(i, base_worker_param)
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
parser.add_argument(
    "-r",
    "--base-runner-params",
    action="store",
    dest="base_runner_param_file_name",
    default="./gssi_experiment/gateway_aggregator/RunnerParameters.json",
    help="The base file that is used to generate runner parameters.",
)

args = parser.parse_args()

with open(args.base_runner_param_file_name, "r", encoding="utf-8") as base_runner_file:
    BASE_WORKER_PARAM: dict = json.loads(base_runner_file.read())

main(BASE_WORKER_PARAM)
