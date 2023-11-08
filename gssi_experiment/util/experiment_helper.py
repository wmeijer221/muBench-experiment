"""
Implements some reusable functionality for experimentation.
"""

import os
from subprocess import Popen
from typing import Dict, Tuple, List, Generator
from time import sleep
import itertools

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

import gssi_experiment.util.doc_helper as doc_helper


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


def run_experiment(
    k8s_parameters_path: str,
    runner_parameter_path: str,
    yaml_builder_path: str,
    pod_initialize_delay: int = 10,
):
    """Experiment runner that depends on a bash script."""
    run_experiment_file = os.path.dirname(__file__) + "/run-full-experiment.sh"
    popen_args = [
        run_experiment_file,
        k8s_parameters_path,
        runner_parameter_path,
        str(pod_initialize_delay),
        yaml_builder_path,
    ]
    print(popen_args)
    proc = Popen(popen_args)
    try:
        proc.wait()
    except KeyboardInterrupt as ex:
        try:
            proc.terminate()
        except OSError:
            pass
        proc.wait()
        raise ex


def run_experiment2(
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
