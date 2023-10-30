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


def visualize_results(data: List[Tuple]):
    """Generates line diagrams with the results."""
    # Dummy data
    # data = [
    #     (0.0, 44, 2801, 732.7795, 376.3061684051299),
    #     (0.125, 32, 2280, 514.15125, 310.8390481799825),
    #     (0.25, 46, 1223, 469.7725, 200.9019991034186),
    #     (0.375, 39, 1382, 453.0955, 251.3497958617631),
    #     (0.5, 34, 1809, 482.2435, 360.3545264149598),
    #     (0.625, 26, 1410, 455.01425, 335.3215248786417),
    #     (0.75, 24, 1389, 458.08675, 194.46708776663854),
    #     (0.875, 40, 1987, 606.1655, 289.84179324202023),
    #     (1.0, 40, 1423, 613.5745, 270.3258107353976),
    # ]

    # Extract data
    s1_intensity, y_min, y_max, y_avg, y_std = zip(*data)

    # Calculate y_std_upper and y_std_lower
    y_std_upper = tuple((e + f for e, f in zip(y_avg, y_std)))
    y_std_lower = tuple((e - f for e, f in zip(y_avg, y_std)))

    # Create a figure with three subplots
    fig, axs = plt.subplots(3, 1, figsize=(8, 12))

    # First subplot with y_avg, y_min, and y_max lines, and filled area around y_avg
    axs[0].fill_between(s1_intensity, y_std_lower, y_std_upper, alpha=0.3, label='std delay')
    axs[0].plot(s1_intensity, y_avg, label='avg delay', color='b')
    axs[0].plot(s1_intensity, y_min, label='min delay', color='g')
    axs[0].plot(s1_intensity, y_max, label='max delay', color='r')
    axs[0].set_title('All Data')
    axs[0].legend()

    # Second subplot with only y_avg line and filled area around it
    axs[1].fill_between(s1_intensity, y_std_lower, y_std_upper, alpha=0.3, label='std delay')
    axs[1].plot(s1_intensity, y_avg, label='avg delay', color='b')
    axs[1].set_title('y_avg')
    axs[1].legend()

    # Third subplot with only y_avg line
    axs[2].plot(s1_intensity, y_avg, label='avg delay', color='b')
    axs[2].set_title('Average Delay')
    axs[2].legend()

    # Add labels and title to the overall figure
    fig.suptitle('S1 Intensity vs. Request Delay')
    plt.tight_layout()
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
