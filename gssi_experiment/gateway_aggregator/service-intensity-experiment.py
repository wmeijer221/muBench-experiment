"""
Runs service intensity experiment and outputs results.

It tests the gateway aggregator deployment with a heterogeneous load to
identify the behaviours in CPU utilization and response delay.
The system deploys four services, three "worker" services (s1, s2, s3) and one
gateway aggregator service which handles aggregate requests. In this context,
a heterogeneous load refers to the weight that is put on the worker services.
As such, requests can be S1-intensive and S3-intensive, respectively describing 
the amount of computation required by either service (i.e., s1 intensive requests 
require a lot of computation by s1 and little by s3). Here, S2 remains unaffected.

This script itself does nothing regarding the deployment topology (meaning that it
does not deploy the three services itself). The muBench deployment / setup is
defined in the various json files contained in this file's containing folder.

This script can be ran with various parameters. For these refer to `./many-experiment.sh`
and the `args_helper`.

The main lifecycle of this script is as follows:
1. Generate template files based on the passed parameters.
2. Iterate through the experiment `steps` number of times (i.e., the number of s1/s3-intensity
   configurations that is considerd; in some sense the granularity of the study.)
3. Create temporary runner parameters (workload etc.) and redeploy the various services.
4. Run the experiment (contained in `experiment_helper` as this is re-used in other experiments.)
5. Calculate some basic statistics.
6. Clean up temporary files.
"""

import datetime
import os
import random
import dotenv

import gssi_experiment.util.doc_helper as doc_helper
import gssi_experiment.util.experiment_helper as exp_helper
import gssi_experiment.util.experiment_visualization_helper as vis_helper
import gssi_experiment.util.args_helper as args_helper

dotenv.load_dotenv()

start_run_message = """

###############################################
####            STARTING NEW RUN            ###
###############################################

"""

print(start_run_message)

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))
print(f"{BASE_FOLDER=}")

parser = args_helper.init_args(BASE_FOLDER)
parser.add_argument(
    "--aggregator-service-path",
    action="store",
    dest="aggregator_service_path",
    default=f"{BASE_FOLDER}/gateway_aggregator_service/service.yaml",
)
args = parser.parse_args()
args.simulation_steps = max(args.simulation_steps, 1)

random.seed(args.seed)
print(f"{args.seed=}")


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
            ),
            (
                # TODO: Move this to `exp_helper.run_experiment2()` to reduce code duplication.
                ["RunnerParameters", "ms_access_gateway"],
                exp_helper.get_server_endpoint(),
            ),
        ],
        editor_type=doc_helper.JsonEditor,
    )


def write_tmp_deployment_template(template: "str | None"):
    # TODO: Move this to `exp_helper.run_experiment2()` to prevent duplicate code.
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
# HACK: This shouldn't be handled with an env variable; it should check for "existing" nodes in the cluster and remove those that aren't present.
if os.getenv("USE_MINIKUBE", "false").lower() == "true" and "minikube" in target_nodes:
    print("Not running in minikube mode, removing it from the possible targets.")
    target_nodes.remove("minikube")

target_nodes = "".join(target_nodes)
equal_distribution_template = equal_distribution_template.format(
    target_nodes=target_nodes
)
# Adding this 'forces' pods to be spread across different nodes
# (this is a bugged k8s feature though as it works during the initial deployment
# but not during re-deployments; i.e., if you want to ensure this, you have to delete
# a deployment, wait for it to be gone, and only then re-apply it; this is a known bug,
# but k8s isn't prioritizing fixing it).
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

node_selector_template = equal_distribution_template

# If it's only one, it will force it to be scheduled on that node.
# Using spread constraints incidentally doesn't work here.
if len(target_nodes) == 1:
    node_selector_template = f"""
        nodeSelector:
            kubernetes.io/hostname: {args.node_selector}
    """


start_time = datetime.datetime.now()

tmp_aggregator_service_path = f'{args.aggregator_service_path}.tmp'
ga_service_yaml_path = (
    exp_helper.write_tmp_service_params_for_node_selector_and_replicas(
        args.aggregator_service_path,
        tmp_aggregator_service_path,
        args.node_selector,
        args.replicas,
    )
)
exp_helper.write_tmp_work_model_for_trials(
    args.base_worker_model_file_name, args.tmp_base_worker_model_file_path, args.trials
)
write_tmp_deployment_template(node_selector_template)
k8s_params_file_path = f"{args.k8s_param_path}.tmp"
exp_helper.write_tmp_k8s_params(
    args.k8s_param_path, k8s_params_file_path, args.cpu_limit, args.replicas
)

# Executes experiments.
experimental_results = []
all_steps = list(range(args.simulation_steps + 1))
random.shuffle(all_steps)
print(f"{all_steps=}")
for i in all_steps:
    write_tmp_runner_params_for_simulation_step(i)
    exp_helper.apply_k8s_yaml_file(ga_service_yaml_path)
    exp_helper.run_experiment2(
        k8s_params_file_path,
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
    output_file_directory=exp_helper.get_output_folder(BASE_FOLDER, args.name),
)

# Clean up temp files.
os.remove(args.tmp_runner_param_file_path)
os.remove(args.tmp_base_worker_model_file_path)
os.remove(k8s_params_file_path)
if os.path.exists(tmp_aggregator_service_path):
    os.remove(tmp_aggregator_service_path)

end_time = datetime.datetime.now()
delta_time = end_time - start_time
print(f"Finished experiment in {str(delta_time)} at {str(end_time)}.")
