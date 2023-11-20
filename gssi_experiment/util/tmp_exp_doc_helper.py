from typing import List, Generator
import itertools

import gssi_experiment.util.doc_helper as doc_helper
import gssi_experiment.util.experiment_helper as exp_helper

def write_tmp_work_model_for_trials(
    base_worker_model_file_name: str,
    tmp_base_worker_model_file_path: str,
    trials: int,
    # TODO: Remove these two defaults
    services: List[str] = ["s1", "s2", "s3"],
    request_types: List[str] = ["s1_intensive", "s3_intensive"],
) -> str:
    """Overwrites the trials field in the WorkModel json file and outputs it to a tmp file."""
    # TODO: get rid of the tmp_base_worker_model_file_path parameter / command-line argument as it's bloat; consider replacing it with `tempfile`.
    base_path = [
        "__service",  # is overwritten
        "internal_service",
        "__request_type",  # is overwritten
        "loader",
        "cpu_stress",
        "trials",
    ]

    def nested_key_generator() -> Generator:
        for service, request_type in itertools.product(services, request_types):
            base_path[0] = service
            base_path[2] = request_type
            yield (base_path, trials)

    base_case = [
        "__service",  # is overwritten
        "internal_service",
        "loader",
        "cpu_stress",
        "trials",
    ]

    def nested_base_case_generator() -> Generator:
        for service in services:
            base_case[0] = service
            yield (base_case, trials)

    overwritten_fields = itertools.chain(
        nested_key_generator(), nested_base_case_generator()
    )

    doc_helper.write_concrete_data_document(
        base_worker_model_file_name,
        tmp_base_worker_model_file_path,
        overwritten_fields=overwritten_fields,
        editor_type=doc_helper.JsonEditor,
    )


def write_tmp_k8s_params(
    input_path: str, output_path: str, cpu_limits: str, replicas: int
):
    overwritten_fields = []
    if replicas > 0:
        replica_field = (["K8sParameters", "replicas"], replicas)
        overwritten_fields.append(replica_field)
    if not cpu_limits is None:
        cpu_limit_field = (["K8sParameters", "cpu-limits"], cpu_limits)
        overwritten_fields.append(cpu_limit_field)
    doc_helper.write_concrete_data_document(
        input_path,
        output_path,
        editor_type=doc_helper.JsonEditor,
        overwritten_fields=overwritten_fields,
    )


def write_tmp_runner_params_for_simulation_step(
    experiment_idx: int, simulation_steps: int, base_runner_param_file_name: str
) -> str:
    """Generates runner params to reflect the s1 intensity setting."""
    step_size = 1.0 / simulation_steps
    intensity = experiment_idx * step_size

    tmp_runner_param_file_path = f"{base_runner_param_file_name}.tmp"
    doc_helper.write_concrete_data_document(
        source_path=base_runner_param_file_name,
        target_path=tmp_runner_param_file_path,
        overwritten_fields=[
            (
                [
                    "RunnerParameters",
                    "HeaderParameters",
                    0,  # NOTE: This assumes the `RequestTypeHeaderFactory` is the first one in the configuration file.
                    "parameters",
                    "probabilities",
                ],
                [intensity, 1.0 - intensity],
            ),
            (
                ["RunnerParameters", "ms_access_gateway"],
                exp_helper.get_server_endpoint(),
            ),
        ],
        editor_type=doc_helper.JsonEditor,
    )
    return tmp_runner_param_file_path
