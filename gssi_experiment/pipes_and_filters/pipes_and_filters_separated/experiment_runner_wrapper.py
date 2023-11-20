"""
Runs service intensity experiment and outputs results.
"""

import os
import random
import dotenv

import gssi_experiment.util.experiment_helper as exp_helper
import gssi_experiment.util.args_helper as args_helper
import gssi_experiment.util.util as util
import gssi_experiment.util.node_selector_helper as ns_helper
import gssi_experiment.util.tmp_exp_doc_helper as tmp_doc_helper

dotenv.load_dotenv()

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
print(f"{BASE_FOLDER=}")

parser = args_helper.init_args(BASE_FOLDER)
args = parser.parse_args()
args.simulation_steps = max(args.simulation_steps, 1)

random.seed(args.seed)
print(f"{args.seed=}")


def run_the_experiment():
    """Does what it says."""

    mubench_k8s_template_folder = os.path.dirname(os.path.dirname(BASE_FOLDER))

    # Overwrites affinity in GA service and muBench service yamls.
    ns_helper.load_and_write_node_affinity_template(args, mubench_k8s_template_folder)
    k8s_params_file_path = f"{args.k8s_param_path}.tmp"
    tmp_doc_helper.write_tmp_k8s_params(
        args.k8s_param_path, k8s_params_file_path, args.cpu_limit, args.replicas
    )

    # Executes experiments for every considered s1 intensity value.
    for step_idx in util.shuffled_range(0, args.simulation_steps + 1, 1):
        tmp_runner_param_file_path = (
            tmp_doc_helper.write_tmp_runner_params_for_simulation_step(
                step_idx, args.simulation_steps, args.base_runner_param_file_name
            )
        )
        exp_params = exp_helper.ExperimentParameters(
            k8s_params_file_path,
            tmp_runner_param_file_path,
            mubench_k8s_template_folder,
            exp_helper.get_output_folder(BASE_FOLDER, args.name, step_idx),
            args.wait_for_pods_delay,
        )
        exp_helper.run_experiment(args, exp_params)


if __name__ == "__main__":
    run_the_experiment()
