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
    "-gw",
    "--gateway-load",
    action="store",
    dest="gateway_load_range",
    default="[0,10]",
    help="The number of simulations that are performed w.r.t. gateway offloading.",
)
args = parser.parse_args()
args.simulation_steps = max(args.simulation_steps, 1)


def write_tmp_runner_params_for_simulation_step(step_idx: int) -> None:
    """1: prepares the experiment."""
    step_size = 1.0 / args.simulation_steps
    rq_type_intensity = step_idx * step_size

    doc_helper.write_concrete_data_document(
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
            )
        ],
        editor_type=doc_helper.JsonEditor,
    )


def write_tmp_work_model_for_offload(gw_offload: int) -> None:
    """Overwrites the "trials" field in the workmodel."""
    gw_offload *= 10

    doc_helper.write_concrete_data_document(
        source_path=args.base_worker_param_file,
        target_path=args.tmp_base_worker_param_file,
        overwritten_fields=[
            (
                ["gw", "internal_service", "loader", "cpu_stress", "range_complexity"],
                [gw_offload, gw_offload],
            ),
            (
                ["s1", "internal_service", "loader", "cpu_stress", "range_complexity"],
                [200 - gw_offload, 200 - gw_offload],
            ),
            (
                ["s2", "internal_service", "loader", "cpu_stress", "range_complexity"],
                [120 - gw_offload, 120 - gw_offload],
            ),
            (
                ["s3", "internal_service", "loader", "cpu_stress", "range_complexity"],
                [150 - gw_offload, 150 - gw_offload],
            ),
        ],
        editor_type=doc_helper.JsonEditor,
    )


start_time = datetime.datetime.now()


# Executes experiments.
(gw_min, gw_max) = (int(ele) for ele in args.gateway_load_range[1:-1].split(","))
experimental_results = []
for i in range(args.simulation_steps + 1):
    for j in range(gw_min, gw_max + 1):
        write_tmp_runner_params_for_simulation_step(i)
        write_tmp_work_model_for_offload(j)
        exp_helper.write_tmp_work_model_for_trials(
            args.tmp_base_worker_model_file_path,
            args.tmp_base_worker_model_file_path,
            args.trials,
        )
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

end_time = datetime.datetime.now()
delta_time = end_time - start_time
print(f"Finished experiment in {str(delta_time)}.")
