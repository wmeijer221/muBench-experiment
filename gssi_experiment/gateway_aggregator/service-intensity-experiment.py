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

random.seed(args.seed)
print(f"{args.seed=}")


def write_tmp_runner_params_for_simulation_step(
    experiment_idx: int, workload_events: int
) -> None:
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
            ),
            (["RunnerParameters", "workload_events"], workload_events),
        ],
        editor_type=doc_helper.JsonEditor,
    )


def write_tmp_deployment_template(template: "str | None"):
    # Reads template base.
    deployment_path = f"{args.yaml_builder_path}/Templates/DeploymentTemplateBase.yaml"
    with open(deployment_path, "r", encoding="utf-8") as base_file:
        data = base_file.read()

    setting = template if template else ""
    data = data.replace("{{NODE_AFFINITY}}", setting)
    # writes data
    deployment_path = f"{args.yaml_builder_path}/Templates/DeploymentTemplate.yaml"
    with open(deployment_path, "w+", encoding="utf-8") as output_file:
        output_file.write(data)


# Runs the experiment

equal_distribution_template = """
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: kubernetes.io/hostname
            operator: In
            values: {target_nodes}
"""
target_node_template = """
            - {name}"""
target_nodes = [
    target_node_template.format(name=node) for node in args.node_selector.split(",")
]
target_nodes = "".join(target_nodes)
equal_distribution_template = equal_distribution_template.format(
    target_nodes=target_nodes
)
# Adding this 'forces' (sort of) nodes to be spread across different nodes.
topology_spread_template = """
  topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: kubernetes.io/hostname
    whenUnsatisfiable: ScheduleAnyway
    labelSelector:
      matchLabels:
        type: {{SERVICE_NAME}}
"""
equal_distribution_template += topology_spread_template


start_time = datetime.datetime.now()

ga_service_yaml_path = (
    exp_helper.write_tmp_service_params_for_node_selector_and_replicas(
        args.aggregator_service_path,
        args.tmp_aggregator_service_path,
        args.node_selector,
        args.replicas,
    )
)
exp_helper.apply_k8s_yaml_file(ga_service_yaml_path)
exp_helper.write_tmp_work_model_for_trials(
    args.base_worker_model_file_name, args.tmp_base_worker_model_file_path, args.trials
)
write_tmp_deployment_template(equal_distribution_template)
k8s_params_file_path = f"{args.k8s_param_path}.tmp"
exp_helper.write_tmp_k8s_params(
    args.k8s_param_path, k8s_params_file_path, args.cpu_limit, args.replicas
)

# Executes experiments.
experimental_results = []
all_steps = list(range(args.simulation_steps + 1))
random.shuffle(all_steps)
print(f"{all_steps=}")
today = datetime.datetime.now()
today = today.strftime("%Y_%m_%d")
for i in all_steps:
    write_tmp_runner_params_for_simulation_step(i, args.workload_events)
    exp_helper.restart_deployment("gateway-aggregator")
    exp_helper.run_experiment2(
        k8s_params_file_path,
        args.tmp_runner_param_file_path,
        args.yaml_builder_path,
        f"{BASE_FOLDER}/results/{today}/{args.name}/{i}_steps/",
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
    output_file_directory=f"{BASE_FOLDER}/results/{today}/{args.name}/",
)

# Clean up temp files.
os.remove(args.tmp_runner_param_file_path)
os.remove(args.tmp_base_worker_model_file_path)
os.remove(k8s_params_file_path)
if os.path.exists(args.tmp_aggregator_service_path):
    os.remove(args.tmp_aggregator_service_path)

end_time = datetime.datetime.now()
delta_time = end_time - start_time
print(f"Finished experiment in {str(delta_time)} at {str(end_time)}.")
