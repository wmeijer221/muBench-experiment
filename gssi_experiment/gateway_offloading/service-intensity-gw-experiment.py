"""Runs service intensity experiment and outputs results."""

import argparse
import datetime
import os

import gssi_experiment.util.json_helper as json_helper
import gssi_experiment.util.experiment_helper as exp_helper


BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
print(f"{BASE_FOLDER=}")


parser = argparse.ArgumentParser()
parser.add_argument(
    "-p",
    "--tmp-runner-param-path",
    action="store",
    dest="tmp_runner_param_file_path",
    default=f"{BASE_FOLDER}/TmpRunnerParameters.json",
    help="File path where the experiments' work models are temporarily stored.",
)
parser.add_argument(
    "-s",
    "--steps",
    type=int,
    action="store",
    dest="simulation_steps",
    default=5,
    help="The number of simulations that are performed w.r.t. request type intensity.",
)
parser.add_argument(
    "-gw",
    "--gateway-load",
    type=int,
    action="store",
    dest="gateway_load_range",
    default="[0,10]",
    help="The number of simulations that are performed w.r.t. gateway offloading.",
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
parser.add_argument(
    "-k",
    "--k8s-param-path",
    action="store",
    dest="k8s_param_path",
    default=f"{BASE_FOLDER}/K8sParameters.json",
    help="Path to the file containing the muBench Kuberenetes parameters.",
)
parser.add_argument(
    "-ybp",
    "--yaml-builder-path",
    action="store",
    dest="yaml_builder_path",
    default=f"{BASE_FOLDER}/",
    help="Specifies the folder in which the yaml template files are stored.",
)
parser.add_argument("--run-once", action="store_true", dest="run_one_step")
args = parser.parse_args()


def write_tmp_runner_params_for_simulation_step(step_idx: int, gw_offload: int) -> None:
    """1: prepares the experiment."""
    step_size = 1.0 / args.simulation_steps
    rq_type_intensity = step_idx * step_size

    gw_offload *= 10

    json_helper.write_concrete_json_document(
        source_path=args.base_runner_param_file_name,
        target_path=args.tmp_runner_param_file_path,
        overwritten_fields=[
            # Sets the request type probability.
            (
                [
                    "RunnerParameters",
                    "HeaderParameters",
                    0,  # NOTE: This assumes the `RequestTypeHeaderFactory` is the first one in the configuration file.
                    "parameters",
                    "probabilities",
                ],
                [rq_type_intensity, 1.0 - rq_type_intensity],
            ),
            # Sets the gateway offload value.
            (
                ["gw", "internal_service", "loader", "cpu_stress", "range_complexity"],
                [gw_offload, gw_offload],
            ),
        ],
    )


args.simulation_steps = max(args.simulation_steps, 1)

start_time = datetime.datetime.now()


# Executes experiments.
(gw_min, gw_max) = (int(ele) for ele in args.gateway_load_range[1:-1].split(","))
experimental_results = []
for i in range(args.simulation_steps + 1):
    for j in range(gw_min, gw_max + 1):
        write_tmp_runner_params_for_simulation_step(i, j)
        exp_helper.run_experiment(
            args.k8s_param_path,
            args.tmp_runner_param_file_path,
            args.yaml_builder_path,
            args.wait_for_pods_delay,
        )
        results = exp_helper.calculate_basic_statistics(i, args.simulation_steps)
        experimental_results.append(results)
        print(f"{i=}: {results=}")

        # For debugging.
        if args.run_one_step:
            print("Stopping because 'run once' flag is set in args.")
            break


# Visualizes results.
print(experimental_results)
exp_helper.visualize_all_data_and_stitch(
    experimental_results, output_file_directory=f"{BASE_FOLDER}/results/"
)

# Clean up temp files.
os.remove(args.tmp_runner_param_file_path)

end_time = datetime.datetime.now()
delta_time = end_time - start_time
print(f"Finished experiment in {str(delta_time)}.")
