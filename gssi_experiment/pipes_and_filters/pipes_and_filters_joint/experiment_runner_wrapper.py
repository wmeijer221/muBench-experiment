"""
Runs service intensity experiment and outputs results.
"""

import os
import random
from typing import Iterator, Tuple, List
import itertools

import dotenv

import gssi_experiment.util.experiment_helper as exp_helper
import gssi_experiment.util.args_helper as args_helper
import gssi_experiment.util.util as util
import gssi_experiment.util.node_selector_helper as ns_helper
import gssi_experiment.util.doc_helper as doc_helper
import gssi_experiment.util.tmp_exp_doc_helper as tmp_doc_helper

dotenv.load_dotenv()

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
print(f"{BASE_FOLDER=}")

parser = args_helper.init_args(BASE_FOLDER)
parser.add_argument("--shared-cpu-limits", action="store", dest="shared_cpu_limits")
args = parser.parse_args()
args.simulation_steps = max(args.simulation_steps, 1)

random.seed(args.seed)
print(f"{args.seed=}")


def write_tmp_work_model() -> str:
    """Writes temporary work model to only increase the cpu limit of the shared services."""
    def nested_key_generator(
        services: "List[str]", limit: str
    ) -> Iterator[Tuple[List[str], str]]:
        base_key = ["__service", "cpu-limits"]
        for service in services:
            base_key[0] = service
            yield (base_key, limit)

    nested_keys = itertools.chain(
        nested_key_generator(["s1", "s2"], args.shared_cpu_limits),
        nested_key_generator(["s3", "s4"], args.cpu_limit),
    )

    base_work_model = f"{BASE_FOLDER}/WorkModel.json"
    tmp_work_model = f"{base_work_model}.tmp"
    doc_helper.write_concrete_data_document(
        base_work_model,
        tmp_work_model,
        overwritten_fields=nested_keys,
        editor_type=doc_helper.JsonEditor,
    )
    return tmp_work_model


def run_the_experiment():
    """Does what it says."""

    mubench_k8s_template_folder = os.path.dirname(os.path.dirname(BASE_FOLDER))

    # Overwrites affinity in GA service and muBench service yamls.
    ns_helper.load_and_write_node_affinity_template(args, mubench_k8s_template_folder)
    k8s_param_path = os.path.dirname(__file__) + "/K8sParameters.json"
    k8s_params_file_path = f"{k8s_param_path}.tmp"
    tmp_doc_helper.write_tmp_k8s_params(
        k8s_param_path, k8s_params_file_path, None, args.replicas
    )

    write_tmp_work_model()

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
            args.data_fetch_delay,
        )
        exp_helper.run_experiment(args, exp_params)


if __name__ == "__main__":
    run_the_experiment()
