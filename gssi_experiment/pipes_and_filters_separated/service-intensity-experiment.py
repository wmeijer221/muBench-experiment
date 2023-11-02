"""Runs service intensity experiment and outputs results."""

import argparse
from os import remove
from subprocess import Popen
from typing import Dict, List, Tuple
from copy import deepcopy
import json
import matplotlib.pyplot as plt
import numpy as np
import datetime
from PIL import Image

BASE_FOLDER = "./gssi_experiment/pipes_and_filters_separated"

def create_worker_params(experiment_idx: int, base_worker_param: dict):
    """1: prepares the experiment."""
    step_size = 1.0 / args.simulation_steps
    freemium_intensity = experiment_idx * step_size

    experiment_params = deepcopy(base_worker_param)
    experiment_params["RunnerParameters"]["HeaderParameters"][0]["parameters"][
        "probabilities"
    ] = [freemium_intensity, 1 - freemium_intensity]

    with open(
        args.temp_worker_param_path, mode="w+", encoding="utf-8"
    ) as temp_work_params:
        print(
            f"experiment-{experiment_idx + 1}/{args.simulation_steps + 1}: {freemium_intensity=}, {temp_work_params.name=}"
        )
        temp_work_params.write(json.dumps(experiment_params, indent=4))
        print(experiment_params)


def run_experiment():
    """2: runs the experiment."""
    popen_args = [
        f"{BASE_FOLDER}/run-full-experiment.sh",
        f"{BASE_FOLDER}/K8sParameters.json",
        args.temp_worker_param_path,
        str(args.wait_for_pods_delay),
    ]
    print(popen_args)
    proc = Popen(popen_args)
    try:
        proc.wait()
    except KeyboardInterrupt as ex:
        proc.kill()
        raise ex


def calculate_results(experiment_idx: int) -> Dict[str, Tuple]:
    """3: processes the results."""

    step_size = 1.0 / args.simulation_steps
    freemium_intensity = experiment_idx * step_size

    all_data_key = "all"

    with open(
        "./SimulationWorkspace/Result/result.txt", "r", encoding="utf-8"
    ) as results_file:
        delays_per_group = {all_data_key: []}
        delays = []
        for entry in results_file:
            elements = entry.split()
            delay = int(elements[1])
            delays_per_group[all_data_key].append(delay)
            # splits my message type
            message_type = list(
                [ele for ele in elements if ele.startswith('"x-requesttype:')]
            )[0]
            message_type = message_type[1:-1].split(":")[1]
            if message_type not in delays_per_group:
                delays_per_group[message_type] = []
            delays_per_group[message_type].append(delay)
        # Calculates basic stats.
        results = {}
        for key, delays in delays_per_group.items():
            mn = np.min(delays)
            mx = np.max(delays)
            avg = np.average(delays)
            std = np.std(delays)
            results[key] = (freemium_intensity, mn, mx, avg, std)
            print(f"{freemium_intensity=}, {key=}: {mn=}, {mx=}, {avg=}, {std=}")
        return results


def visualize_all_results(data: List[Dict[str, Tuple]]) -> List[str]:
    """Generates plots for each data type."""
    # Dummy data
    # data = [
    #     {
    #         "all": (0.0, 357, 1845, 914.93, 420.83691033463305),
    #         "s3_intensive": (0.0, 357, 1845, 914.93, 420.83691033463305),
    #     },
    #     {
    #         "all": (0.3333333333333333, 166, 1309, 570.61, 270.60383940365665),
    #         "s1_intensive": (
    #             0.3333333333333333,
    #             166,
    #             1215,
    #             572.1142857142858,
    #             309.6711409062912,
    #         ),
    #         "s3_intensive": (0.3333333333333333, 188, 1309, 569.8, 247.01773215702553),
    #     },
    #     {
    #         "all": (0.6666666666666666, 163, 1603, 717.14, 320.8091650810494),
    #         "s1_intensive": (
    #             0.6666666666666666,
    #             163,
    #             1472,
    #             700.6716417910447,
    #             299.40849089445106,
    #         ),
    #         "s3_intensive": (
    #             0.6666666666666666,
    #             190,
    #             1603,
    #             750.5757575757576,
    #             358.0479086195733,
    #         ),
    #     },
    #     {
    #         "all": (1.0, 261, 1445, 659.22, 322.52617196128443),
    #         "s1_intensive": (1.0, 261, 1445, 659.22, 322.52617196128443),
    #     },
    # ]
    # Collects relevant keys
    keys = set()
    for ele in data:
        for key in ele:
            keys.add(key)
    # visualizes data for each key.
    fig_names = []
    for key in keys:
        key_data = []
        for ele in data:
            if not key in ele:
                continue
            dpoint = ele[key]
            key_data.append(dpoint)
        fig_name = visualize_results(key_data, output_file_name=key)
        fig_names.append(fig_name)
    return fig_names


def visualize_results(data: List[Tuple], output_file_name) -> str:
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
    freemium_intensity, y_min, y_max, y_avg, y_std = zip(*data)

    # Calculate y_std_upper and y_std_lower
    y_std_upper = tuple((e + f for e, f in zip(y_avg, y_std)))
    y_std_lower = tuple((e - f for e, f in zip(y_avg, y_std)))

    # Create a figure with three subplots
    fig, axs = plt.subplots(3, 1, figsize=(8, 12))

    # First subplot with y_avg, y_min, and y_max lines, and filled area around y_avg
    axs[0].fill_between(
        freemium_intensity, y_std_lower, y_std_upper, alpha=0.3, label="std delay"
    )
    axs[0].plot(freemium_intensity, y_avg, label="avg delay", color="g")
    axs[0].plot(freemium_intensity, y_min, label="min delay", color="b")
    axs[0].plot(freemium_intensity, y_max, label="max delay", color="orange")
    axs[0].set_title("All Data")
    axs[0].set_ylabel("Delay (ms)")
    axs[0].set_xlabel("Freemium Intensity")
    axs[0].legend()

    # Second subplot with only y_avg line and filled area around it
    axs[1].fill_between(
        freemium_intensity, y_std_lower, y_std_upper, alpha=0.3, label="std delay"
    )
    axs[1].plot(freemium_intensity, y_avg, label="avg delay", color="g")
    axs[1].set_title("Average Delay + Standard Deviation")
    axs[1].set_ylabel("Delay (ms)")
    axs[1].set_xlabel("Freemium Intensity")
    axs[1].legend()

    # Third subplot with only y_avg line
    axs[2].plot(freemium_intensity, y_avg, label="avg delay", color="g")
    axs[2].set_title("Average Delay")
    axs[2].set_ylabel("Delay (ms)")
    axs[2].set_xlabel("Freemium Intensity")
    axs[2].legend()

    # Add labels and title to the overall figure
    fig.suptitle(f"Freemium Intensity vs. Request Delay ({output_file_name})")
    plt.tight_layout()
    fig_name = f"{BASE_FOLDER}/figure_{output_file_name}.png"
    plt.savefig(fig_name)
    return fig_name


def stitch_figures(image_paths: List[str]):
    """Stitches multiple figures together horizontally."""
    # sorts image path names.
    image_paths = sorted(image_paths)

    # Open and load all the images
    images = [Image.open(image_path) for image_path in image_paths]

    # Get the widths and heights of all images
    widths, heights = zip(*(i.size for i in images))

    # Calculate the total width and height for the new image
    total_width = sum(widths)
    max_height = max(heights)

    # Create a new image with the calculated size
    new_image = Image.new("RGB", (total_width, max_height))

    # Paste the images horizontally
    x_offset = 0
    for image in images:
        new_image.paste(image, (x_offset, 0))
        x_offset += image.width

    # Save the resulting image
    output_file_name = f"{BASE_FOLDER}/figure.png"
    new_image.save(output_file_name)

    # Close the images
    for image in images:
        image.close()

    print(f"Images stitched and saved as '{output_file_name}'.")


def main(base_worker_param: dict):
    """Runs complete experiment."""
    experimental_results = []

    start_time = datetime.datetime.now()

    # executes experiments.
    for i in range(args.simulation_steps + 1):
        create_worker_params(i, base_worker_param)
        run_experiment()
        results = calculate_results(i)
        experimental_results.append(results)
        print(f"{i=}: {results=}")

    # visualizes results.
    print(experimental_results)
    fig_names = visualize_all_results(experimental_results)
    stitch_figures(fig_names)

    # 5: cleanup
    remove(args.temp_worker_param_path)
    for fig_name in fig_names:
        remove(fig_name)

    end_time = datetime.datetime.now()
    delta_time = end_time - start_time
    print(f"Finished experiment in {str(delta_time)}.")


parser = argparse.ArgumentParser()
parser.add_argument(
    "-p",
    "--tmp-worker-param-path",
    action="store",
    dest="temp_worker_param_path",
    default=f"{BASE_FOLDER}/tmp_work_model.json",
    help="File path where the experiments' work models are temporarily stored.",
)
parser.add_argument(
    "-s",
    "--steps",
    type=int,
    action="store",
    dest="simulation_steps",
    default=5,
    help="The number of simulations that are performed w.r.t. Freemium Intensity.",
)
parser.add_argument(
    "-r",
    "--base-runner-params",
    action="store",
    dest="base_runner_param_file_name",
    default=f"{BASE_FOLDER}/RunnerParameters.json",
    help="The base file that is used to generate runner parameters.",
)
parser.add_argument(
    "-w",
    "--wait-for-pods",
    action="store",
    dest="wait_for_pods_delay",
    type=int,
    default=10,
    help="The number of seconds that we will wait for pods to start.",
)

args = parser.parse_args()

with open(args.base_runner_param_file_name, "r", encoding="utf-8") as base_runner_file:
    BASE_WORKER_PARAM: dict = json.loads(base_runner_file.read())

main(BASE_WORKER_PARAM)
