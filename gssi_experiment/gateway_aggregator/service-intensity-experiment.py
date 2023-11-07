"""Runs service intensity experiment and outputs results."""

import datetime
import os

import gssi_experiment.util.doc_helper as doc_helper
import gssi_experiment.util.experiment_helper as exp_helper
import gssi_experiment.util.args_helper as args_helper

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
print(f"{BASE_FOLDER=}")

parser = args_helper.init_args(BASE_FOLDER)
parser.add_argument(
    "--aggregator-service-path",
    action="store",
    dest="aggregator_service_path",
    default=f"{BASE_FOLDER}/gateway_aggregator_service/service.yaml",
)
parser.add_argument(
    "--tmp-aggregator-service-path",
    action="store",
    dest="tmp_aggregator_service_path",
    default=f"{BASE_FOLDER}/tmp_service.yaml",
)
args = parser.parse_args()
args.simulation_steps = max(args.simulation_steps, 1)


def write_tmp_runner_params_for_simulation_step(experiment_idx: int) -> None:
    """1: prepares the experiment."""
    step_size = 1.0 / args.simulation_steps
    s1_intensity = experiment_idx * step_size

    doc_helper.write_concrete_data_document(
        source_path=args.base_runner_param_file_name,
        target_path=args.tmp_runner_param_file_path,
        overwritten_fields=[
            (
                [
                    "RunnerParameters",
                    "HeaderParameters",
                    0,  # NOTE: This assumes the `RequestTypeHeaderFactory` is the first one in the configuration file.
                    "parameters",
                    "probabilities",
                ],
                [s1_intensity, 1.0 - s1_intensity],
            )
        ],
        editor_type=doc_helper.JsonEditor,
    )


def write_tmp_service_params_for_node_selector(target_node: "str | None") -> str:
    if target_node is None:
        return args.aggregator_service_path
    doc_helper.write_concrete_data_document(
        args.aggregator_service_path,
        args.tmp_aggregator_service_path,
        overwritten_fields=[
            (
                # NOTE: Assumes the Deployment entity has index 3.
                [3, "spec", "template", "spec", "nodeSelector"],
                {"kubernetes.io/hostname": target_node},
            )
        ],
        editor_type=doc_helper.YamlEditor,
    )
    return args.tmp_aggregator_service_path


# Runs the experiment

start_time = datetime.datetime.now()

ga_service_yaml_path = write_tmp_service_params_for_node_selector(args.node_selector)
exp_helper.apply_k8s_yaml_file(ga_service_yaml_path)

# Executes experiments.
experimental_results = []
for i in range(args.simulation_steps + 1):
    write_tmp_runner_params_for_simulation_step(i)
    exp_helper.restart_deployment("gateway-aggregator")
    exp_helper.run_experiment2(
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
if os.path.exists(args.tmp_aggregator_service_path):
    os.remove(args.tmp_aggregator_service_path)

end_time = datetime.datetime.now()
delta_time = end_time - start_time
print(f"Finished experiment in {str(delta_time)}.")
