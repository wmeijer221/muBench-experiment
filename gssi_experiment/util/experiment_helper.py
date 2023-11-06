"""
Implements some reusable functionality for experimentation.
"""

import os
from subprocess import Popen
from typing import Dict, Tuple, List

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def run_experiment(
    k8s_parameters_path: str,
    runner_parameter_path: str,
    pod_initialize_delay: int = 10,
):
    """2: runs the experiment."""
    run_experiment_file = os.path.dirname(__file__) + "/run-full-experiment.sh"
    popen_args = [
        run_experiment_file,
        k8s_parameters_path,
        runner_parameter_path,
        str(pod_initialize_delay),
    ]
    print(popen_args)
    proc = Popen(popen_args)
    try:
        proc.wait()
    except KeyboardInterrupt:
        try:
            proc.terminate()
        except OSError:
            pass
        proc.wait()


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


def visualize_all_results(
    data: List[Dict[str, Tuple]], output_file_directory: str
) -> List[str]:
    """Generates plots for each data type."""
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
        output_file_path = f"{output_file_directory}/figure_{key}.png"
        visualize_results(key_data, figure_name=key, output_file_path=output_file_path)
        fig_names.append(output_file_path)
    return fig_names


def visualize_results(
    data: List[Tuple], figure_name: str, output_file_path: str
) -> None:
    """Generates line diagrams with the results."""
    # Extract data
    s1_intensity, y_min, y_max, y_avg, y_std = zip(*data)

    # Calculate y_std_upper and y_std_lower
    y_std_upper = tuple((e + f for e, f in zip(y_avg, y_std)))
    y_std_lower = tuple((e - f for e, f in zip(y_avg, y_std)))

    # Create a figure with three subplots
    fig, axs = plt.subplots(3, 1, figsize=(8, 12))

    # First subplot with y_avg, y_min, and y_max lines, and filled area around y_avg
    axs[0].fill_between(
        s1_intensity, y_std_lower, y_std_upper, alpha=0.3, label="std delay"
    )
    axs[0].plot(s1_intensity, y_avg, label="avg delay", color="g")
    axs[0].plot(s1_intensity, y_min, label="min delay", color="b")
    axs[0].plot(s1_intensity, y_max, label="max delay", color="orange")
    axs[0].set_title("All Data")
    axs[0].set_ylabel("Delay (ms)")
    axs[0].set_xlabel("S1 Intensity")
    axs[0].legend()

    # Second subplot with only y_avg line and filled area around it
    axs[1].fill_between(
        s1_intensity, y_std_lower, y_std_upper, alpha=0.3, label="std delay"
    )
    axs[1].plot(s1_intensity, y_avg, label="avg delay", color="g")
    axs[1].set_title("Average Delay + Standard Deviation")
    axs[1].set_ylabel("Delay (ms)")
    axs[1].set_xlabel("S1 Intensity")
    axs[1].legend()

    # Third subplot with only y_avg line
    axs[2].plot(s1_intensity, y_avg, label="avg delay", color="g")
    axs[2].set_title("Average Delay")
    axs[2].set_ylabel("Delay (ms)")
    axs[2].set_xlabel("S1 Intensity")
    axs[2].legend()

    # Add labels and title to the overall figure
    fig.suptitle(f"S1 Intensity vs. Request Delay ({figure_name})")
    plt.tight_layout()

    output_dir = os.path.dirname(output_file_path)
    if not os.path.exists(output_dir):
        print(f'Creating directory "{output_dir}".')
        os.makedirs(output_dir)
    plt.savefig(output_file_path)


def stitch_figures(image_paths: List[str], output_file_name: str):
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
    # output_file_name = f"{BASE_FOLDER}/figure.png"
    new_image.save(output_file_name)

    # Close the images
    for image in images:
        image.close()

    print(f"Images stitched and saved as '{output_file_name}'.")


def visualize_all_data_and_stitch(
    data: List[Dict[str, Tuple]],
    output_file_directory: str,
    stitched_file_name: str = "figure_stitched",
    delete_after_stitch: bool = True,
):
    """Outputs all data and stitches the resulting figures together."""
    fig_names = visualize_all_results(data, output_file_directory)
    output_file_name = f"{output_file_directory}/{stitched_file_name}.png"
    stitch_figures(fig_names, output_file_name)
    if delete_after_stitch:
        for fig_name in fig_names:
            os.remove(fig_name)
