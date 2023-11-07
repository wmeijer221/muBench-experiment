import argparse


def init_args(base_folder) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    # muBench k8s
    parser.add_argument(
        "--k8s-param-path",
        action="store",
        dest="k8s_param_path",
        default=f"{base_folder}/K8sParameters.json",
        help="Path to the file containing the muBench Kuberenetes parameters.",
    )
    parser.add_argument(
        "--yaml-builder-path",
        action="store",
        dest="yaml_builder_path",
        default="./gssi_experiment/gateway_aggregator/",
        help="Specifies the folder in which the yaml template files are stored.",
    )
    # TODO: implement this.
    parser.add_argument(
        "--node-selector",
        action="store",
        dest="node_selector",
        default=None,
        help="The node on which the pods must be deployed.",
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


