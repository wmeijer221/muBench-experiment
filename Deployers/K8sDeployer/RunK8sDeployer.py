import sys
import os
import json
import shutil

from time import sleep

# appending a path
sys.path.append("../../")

import K8sYamlBuilder as K8sYamlBuilder
import K8sYamlDeployer as K8sYamlDeployer

import argparse
import argcomplete


def main():
    ### Functions
    def create_deployment_config():
        print("---")
        try:
            with open(workmodel_path) as f:
                workmodel = json.load(f)
        except Exception as err:
            print("ERROR: in RunK8sDeployer,", err)
            exit(1)
        K8sYamlBuilder.customization_work_model(workmodel, k8s_parameters)
        K8sYamlBuilder.create_deployment_yaml_files(
            workmodel,
            k8s_parameters,
            nfs_conf,
            builder_module_path,
            args.yaml_builder_path,
        )
        created_items = os.listdir(f"{builder_module_path}/yamls")
        print(f"Stored the files in {builder_module_path}/yamls")
        print(f"The following files are created: {created_items}")
        print("---")
        # return a list of the files just created
        return created_items, workmodel

    def remove_files(folder_v):
        try:
            folder_items = os.listdir(folder_v)
            print("######################")
            print(f"Removing files in: {folder_v}")
            print("######################")
            for item in folder_items:
                file_path = f"{folder_v}/{item}"
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Removed file: {item}")
            print("---")
        except Exception as er:
            print("######################")
            print(f"Error removing following files: {er}")
            print("######################")

    ### Main

    k8s_Builder_PATH = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config-file",
        action="store",
        dest="parameters_file",
        help="The K8s Parameters file",
        default=f"{k8s_Builder_PATH}/K8sParameters.json",
    )
    parser.add_argument(
        "-y",
        "--yes-undeploy",
        action="store_true",
        dest="undeploy_without_prompt",
        help="If enabled, services are undeployed without a confirmation prompt.",
    )
    parser.add_argument(
        "-r",
        "--auto-redeploy",
        action="store_true",
        dest="auto_redeploy",
        help="If enabled, services are automatically redeployed after they are undeployed.",
    )
    parser.add_argument(
        "-cl",
        "--clean-deployment",
        action="store_true",
        dest="clean_deployment",
        help="When used, the old deployment is cleaned up.",
    )
    parser.add_argument(
        "-ybp",
        "--yaml-builder-path",
        action="store",
        dest="yaml_builder_path",
        default=None,
        help="Specifies the folder in which the yaml template files are stored.",
    )

    argcomplete.autocomplete(parser)

    try:
        args = parser.parse_args()
    except ImportError:
        print(
            "Import error, there are missing dependencies to install.  'apt-get install python3-argcomplete "
            "&& activate-global-python-argcomplete3' may solve"
        )
    except AttributeError:
        parser.print_help()
    except Exception as err:
        print("Error:", err)

    #### input params
    parameters_file_path = args.parameters_file

    try:
        with open(parameters_file_path) as f:
            params = json.load(f)
        k8s_parameters = params["K8sParameters"]
        nfs_conf = dict()
        internal_service_functions_file_path = params["InternalServiceFilePath"]
        workmodel_path = params["WorkModelPath"]

        if "OutputPath" in params.keys() and len(params["OutputPath"]) > 0:
            output_path = params["OutputPath"]
            if output_path.endswith("/"):
                output_path = output_path[:-1]
            if not os.path.exists(output_path):
                os.makedirs(output_path)
        else:
            output_path = None

    except Exception as err:
        print("ERROR: in RunK8sDeployer,", err)
        exit(1)

    ###  Create YAML, insert files (workmodel.json and custom function) as configmaps, and deploy YAML

    folder_not_exist = False
    if output_path is None:
        builder_module_path = K8sYamlBuilder.DEFAULT_K8s_YAML_BUILDER_PATH
    else:
        builder_module_path = output_path
    if not os.path.exists(f"{builder_module_path}/yamls"):
        folder_not_exist = True
    folder = f"{builder_module_path}/yamls"

    if (folder_not_exist or len(os.listdir(folder)) == 0) and not args.clean_deployment:
        # keyboard_input = input("\nDirectory empty, wanna DEPLOY? (y)").lower() or "y"
        keyboard_input = "y"

        if keyboard_input == "y" or keyboard_input == "yes":
            # Create YAML files
            updated_folder_items, work_model = create_deployment_config()
            # Create and deploy configmaps for internal service custom function and workmodel.json
            K8sYamlDeployer.deploy_configmap(
                k8s_parameters,
                K8sYamlDeployer.create_workmodel_configmap_data(
                    k8s_parameters, work_model
                ),
            )
            K8sYamlDeployer.deploy_configmap(
                k8s_parameters,
                K8sYamlDeployer.create_internal_service_configmap_data(params),
            )
            # Deploy YAML files
            K8sYamlDeployer.deploy_nginx_gateway(folder)
            K8sYamlDeployer.deploy_items(folder, st=k8s_parameters["sleep"])
        else:
            print("...\nOk you do not want to DEPLOY stuff! Bye!")
    else:
        print("######################")
        print("!!!! Warning !!!!")
        print("######################")
        print(f"Folder is not empty: {folder}.")
        undeploy = args.undeploy_without_prompt
        if not args.undeploy_without_prompt:
            keyboard_input = (
                input(
                    "Do you want to UNDEPLOY yamls of the old application first, delete the files and then start the new applicaiton ? (n) "
                )
                or "n"
            )
        if (
            args.undeploy_without_prompt
            or keyboard_input == "y"
            or keyboard_input == "yes"
        ):
            K8sYamlDeployer.undeploy_items(folder)
            # K8sYamlDeployer.undeploy_nginx_gateway(folder)
            K8sYamlDeployer.undeploy_configmap("internal-services", k8s_parameters)
            K8sYamlDeployer.undeploy_configmap("workmodel", k8s_parameters)
            remove_files(folder)

            if args.auto_redeploy:
                print("######################")
                print("Automatically redeploying in 30 seconds!")
                print("######################")
                sleep(30)
                main()
        else:
            print("...\nOk you want to keep the OLD application! Bye!")


if __name__ == "__main__":
    main()
