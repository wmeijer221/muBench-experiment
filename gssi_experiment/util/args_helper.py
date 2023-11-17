import argparse
from sys import argv


def init_args(base_folder) -> argparse.ArgumentParser:
    print(f"{argv=}")

    parser = argparse.ArgumentParser()

    # General
    parser.add_argument(
        "--seed",
        action="store",
        dest="seed",
        default=0,
        help="The seed used for random operations.",
    )
    parser.add_argument(
        "--name",
        action="store",
        dest="name",
        default="",
        help="special name for the experiment to allow diversification.",
    )
    # muBench k8s
    parser.add_argument(
        "--k8s-param-path",
        action="store",
        dest="k8s_param_path",
        default=f"{base_folder}/K8sParameters.json",
        help="Path to the file containing the muBench Kuberenetes parameters.",
    )
    parser.add_argument(
        "--node-selector",
        action="store",
        dest="node_selector",
        default="minikube",
        help="The node on which the pods must be deployed.",
    )
    parser.add_argument(
        "--workload-events",
        action="store",
        dest="workload_events",
        default=500,
        type=int,
        help="The number of requests sent to the system.",
    )
    parser.add_argument(
        "--cpu-limit", action="store", dest="cpu_limit", default="1000m"
    )
    parser.add_argument(
        "--replicas", action="store", dest="replicas", default=1, type=int
    )

    # Dynamic muBench runner params
    parser.add_argument(
        "--base-runner-params",
        action="store",
        dest="base_runner_param_file_name",
        default=f"{base_folder}/RunnerParameters.json",
        help="The base file that is used to generate runner parameters.",
    )
    parser.add_argument(
        "--tmp-runner-param-path",
        action="store",
        dest="tmp_runner_param_file_path",
        default=f"{base_folder}/TmpRunnerParameters.json",
        help="File path where the experiments' work models are temporarily stored.",
    )

    parser.add_argument(
        "--base-worker-model",
        action="store",
        dest="base_worker_model_file_name",
        default=f"{base_folder}/WorkModel.json",
        help="The base file for the work model.",
    )
    parser.add_argument(
        "--tmp-base-worker-model-path",
        action="store",
        dest="tmp_base_worker_model_file_path",
        default=f"{base_folder}/TmpWorkModel.json",
        help="The base file for the work model.",
    )
    parser.add_argument(
        "-t",
        "--trials",
        action="store",
        dest="trials",
        default=20,
        type=int,
        help="Amplifier value for CPU load of muBench services.",
    )

    # Experiment params
    parser.add_argument(
        "-s",
        "--steps",
        type=int,
        action="store",
        dest="simulation_steps",
        default=5,
        help="The number of simulations that are performed w.r.t. S1 intensity.",
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

    parser.add_argument("--run-once", action="store_true", dest="run_one_step")

    return parser
