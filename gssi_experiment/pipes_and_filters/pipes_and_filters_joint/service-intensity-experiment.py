"""
Runs service intensity experiment and outputs results.
It accounts for heterogeneous requests and different amounts of tasks offloaded to the gateway.
"""

import datetime
import os
import random

import gssi_experiment.util.doc_helper as doc_helper
import gssi_experiment.util.experiment_helper as exp_helper
import gssi_experiment.util.experiment_visualization_helper as vis_helper
import gssi_experiment.util.args_helper as args_helper

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
print(f"{BASE_FOLDER=}")


parser = args_helper.init_args(BASE_FOLDER)
args = parser.parse_args()
args.simulation_steps = max(args.simulation_steps, 1)

random.seed(args.seed)
print(f"{args.seed=}")


def write_tmp_runner_params_for_simulation_step(step: int) -> str:
    """1: prepares the experiment."""
    step_size = 1.0 / args.simulation_steps
    rq_type_intensity = step * step_size

    tmp_runner_param_file = f"{args.base_runner_param_file_name}.tmp"
    doc_helper.write_concrete_data_document(
        source_path=args.base_runner_param_file_name,
        target_path=tmp_runner_param_file,
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
            (
                # TODO: move this to `run_experiment2()` to avoid duplicate code in experiment files.
                ["RunnerParameters", "ms_access_gateway"],
                exp_helper.get_server_endpoint(),
            ),
        ],
        editor_type=doc_helper.JsonEditor,
    )
    return tmp_runner_param_file



start_time = datetime.datetime.now()

# Overwrites work model and k8s params file.
exp_helper.write_tmp_work_model_for_trials(
    args.base_worker_model_file_name, args.tmp_base_worker_model_file_path, args.trials
)
k8s_params_file_path = f"{args.k8s_param_path}.tmp"
exp_helper.write_tmp_k8s_params(
    args.k8s_param_path, k8s_params_file_path, args.cpu_limit, args.replicas
)

# Executes experiments.
(gw_min, gw_max, gw_step) = (
    int(ele) for ele in args.gateway_load_range[1:-1].split(",")
)
gateway_steps = list(range(gw_min, gw_max + 1, gw_step))
print(f"gateway range / interval: {gateway_steps}")
for gateway_offload in gateway_steps:
    experimental_results = []

    # Generates the list of considered simulation steps.
    all_steps = list(range(args.simulation_steps + 1))
    random.shuffle(all_steps)
    print(f"{all_steps=}")

    for step_idx in all_steps:
        tmp_runner_param_file_path = write_tmp_runner_params_for_simulation_step(
            step_idx
        )
        tmp_base_worker_model_file_path = f"{args.base_worker_model_file_name}.tmp"
        exp_helper.write_tmp_work_model_for_trials(
            args.base_worker_model_file_name,
            tmp_base_worker_model_file_path,
            args.trials,
            services=["s1", "s2", "s3", "s4"],
            request_types=['dashboard', 'monitoring'],
        )
        output_folder = exp_helper.get_output_folder(BASE_FOLDER, args.name, step_idx)
        output_folder = f"{output_folder}/{gateway_offload}_offload/"
        exp_helper.run_experiment2(
            args.k8s_param_path,
            tmp_runner_param_file_path,
            args.yaml_builder_path,
            output_folder,
            args.wait_for_pods_delay,
        )
        results = exp_helper.calculate_basic_statistics(step_idx, args.simulation_steps)
        experimental_results.append(results)
        print(f"{step_idx=}: {results=}")

        # For debugging.
        if args.run_one_step:
            print("Stopping because 'run once' flag is set in args.")
            break

    # Visualizes results.
    print(experimental_results)
    vis_helper.visualize_all_data_and_stitch(
        experimental_results,
        output_file_directory=exp_helper.get_output_folder(BASE_FOLDER, args.name),
        stitched_file_name=f"figure_stitched_gw_{gateway_offload}",
    )

# Clean up temp files.
os.remove(tmp_runner_param_file_path)
os.remove(tmp_base_worker_model_file_path)

end_time = datetime.datetime.now()
delta_time = end_time - start_time
print(f"Finished experiment in {str(delta_time)}.")
