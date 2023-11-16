"""Runs service intensity experiment and outputs results."""

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

random.seed(args.seed)
print(f"{args.seed=}")


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
            ),
            (["RunnerParameters", "workload_events"], args.workload_events),
            (
                # TODO: move this to `run_experiment2()` to avoid duplicate code in experiment files.
                ["RunnerParameters", "ms_access_gateway"],
                exp_helper.get_server_endpoint(),
            ),
        ],
        editor_type=doc_helper.JsonEditor,
    )


def write_tmp_work_model_for_offload(gw_offload: int) -> None:
    """Overwrites the "trials" field in the workmodel."""
    gw_offload *= 10

    doc_helper.write_concrete_data_document(
        source_path=args.base_worker_model_file_name,
        target_path=args.tmp_base_worker_model_file_path,
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

exp_helper.write_tmp_work_model_for_trials(
    args.base_worker_model_file_name, args.tmp_base_worker_model_file_path, args.trials
)
k8s_params_file_path = f"{args.k8s_param_path}.tmp"
exp_helper.write_tmp_k8s_params(
    args.k8s_param_path, k8s_params_file_path, args.cpu_limit, args.replicas
)

# Executes experiments.write_tmp_deployment_template
(gw_min, gw_max, gw_step) = (int(ele) for ele in args.gateway_load_range[1:-1].split(","))
gateway_steps = list(range(gw_min, gw_max + 1, gw_step))
print(f'gateway range / interval: {gateway_steps}')
for j in gateway_steps:
    experimental_results = []
    all_steps = list(range(args.simulation_steps + 1))
    random.shuffle(all_steps)
    print(f"{all_steps=}")
    for i in all_steps:
        write_tmp_runner_params_for_simulation_step(i)
        write_tmp_work_model_for_offload(j)
        exp_helper.write_tmp_work_model_for_trials(
            args.tmp_base_worker_model_file_path,
            args.tmp_base_worker_model_file_path,
            args.trials,
            services=['gw', 's1', 's2', 's3'],
            request_types=[]
        )
        exp_helper.run_experiment2(
            args.k8s_param_path,
            args.tmp_runner_param_file_path,
            args.yaml_builder_path,
            exp_helper.get_output_folder(BASE_FOLDER, args.name, i),
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
    vis_helper.visualize_all_data_and_stitch(
        experimental_results,
        output_file_directory=f"{BASE_FOLDER}/results/",
        stitched_file_name=f"figure_stitched_gw_{j * 10}",
    )

# Clean up temp files.
os.remove(args.tmp_runner_param_file_path)

end_time = datetime.datetime.now()
delta_time = end_time - start_time
print(f"Finished experiment in {str(delta_time)}.")
