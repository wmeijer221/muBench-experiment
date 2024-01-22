# Replication Package

This replication package is part of the study _Meijer, Trubiani, and Aleti. "Experimental evaluation of architectural software performance design patterns in microservices"_ which was performed as part of a research internship at the Gran Sasso Science Institute (GSSI) in L'Aquila, Italy.

_If anything is unclear, feel free to contact me at `research@wmeijer.com`._

The foundation of this study lies in two studies in particular:

- The theoretical models for performance design patterns: _Pinciroli et al. (2023) "Performance Modeling and Analysis of Design Patterns for Microservice Systems."_
- The muBench benchmarking system: _Detti et al. (2023) "μBench: An Open-Source Factory of Benchmark Microservice Applications."_

## Installation guide

As the experiment is run on a real cluster, the installation guide is not completely trivial.
Two main technologies are used to set up a Kubernetes cluster: OpenStack and [k3s](https://docs.k3s.io/quick-start).
Of these, only k3s needed to be set up in this study as the OpenStack environment was directly available.
Simply put, k3s is an easy-to-use variant of Kubernetes that preselects things such as the network controller, designed for small-scale clusters and edge devices.

This experiment defined three large compute nodes and one `xl` compute node running `Ubuntu-22.04-x86_64-2022-11-13` (though, in the end only one `large` and the one `xl` node were used).
When doing this, there are several things to consider: 1) setting up a key pair to allow access through SSH, 2) configuring the system's firewall to allow ingress data on ports `22` (SSH), `6443` (kubectl), `31113` (for the deployed apps in this experiment) and `30000-30003` (for muBench monitoring), and 3) defining some floating IPs to grant access to the different nodes from your local device.
After you have set up several compute nodes in your OpenStack environment, you can install k3s by simply following the instructions on their quick-start page (you can easily do this by SSH-ing into the different nodes).

Then, to connect to the cluster from your local device, copy the config file of the master node (stored in `/etc/rancher/k3s/k3s.yaml`) on your local device (as `~/.kube/config`).
On your local device, change the IP address of the server to one of the floating IPs you created in OpenStack.
You should be able to run commands like `kubectl get nodes` locally now.
To set up the monitoring tools issues by `muBench`, simply follow the instructions in the [manual](../Docs/Manual.md#install-and-access-the-monitoring-framework), which can be summarized to run: `./Monitoring/kubernetes-full-monitoring/monitoring-install.sh`.
This enables Prometheus, Kiali, and Jaeger.
[This script](./bash/setup-k8s-control-panel.sh) could be helpful for this as well (it's mostly a reference, running the script probably won't work as it doesn't set the Kubernetes config files for you).

This study used a dedicated compute node for load generation.
To set this up, simply add another node in OpenStack, and run [its setup script](./bash/setup-client-node.sh).
After, copy the Kubernetes config file (the one you created in the previous step) to this node (just paste its contents into `~/.kube/config`; the file should already be there if you run the bash script).

## Running experiments

Before running an experiment, make sure that your `.env` is set up properly.
For this, copy the `example.env` file to `.env` and update the `SERVER_API_ENDPOINT` and `PROMETHEUS_API_ENDPOINT` to specify the right IP address (this is the main floating IP of your Kubernetes cluster; though the internal IP should work too).
Don't forget to specify their ports as well (`31113` and `30000`, respectively).
If you're running the experiment on Minikube, make sure to set `USE_MINIKUBE` to `true`.
If you're not, either remove it or set it to `false`.
At some point, we ran into issues with the DNS resolver for which none of the requests could arrive.
If you do too, update the `K8S_DNS_RESOLVER` to specify the IP address of the `coredns` pod.

To run all of the experiments, simply run `./gssi_experiment/bash/run-all-small-experiments.sh`.
To run any individual experiment, navigate to the design pattern's respective folder, and run `experiment-small.sh`.
The bash script is simply used to automate replications, the actual experimental set-up is written in the `experiment_runner_wrapper.py` files.
Each of these files implements the general lifecycle of an experiment (e.g., iterating through different heterogeneous load configurations, and generating temporary configuration files).

These scripts themselves do not directly launch the various muBench services.
This is done in [the experiment helper](./util/experiment_helper.py) where `run_experiment` implements the common lifecycle of running an experiment.
Before running an experiment, make sure that prometheus is running.
If you forgot to do this and therefore no Prometheus data is collected, you can use [This notebook](./gssi_experiment/util/posterior_prometheus_fetcher.ipynb); this is a very unsustainable method of getting the CPU utilization data, however.

_Currently, there is a bug when running the experiments on a Minikube cluster. In that case, the `node-selector` field in `experiment-small.sh` needs to be changed to just `minikube`. If you're doing this in Minikube, make sure that the `USE_MINIKUBE` field in your `.env` file is set to true._

When experiments are finished running (which takes some time), the experiments' results are stored in their respective `results/pinciroli_replication_fin/` folders.
To download the theoretical results, run `./gssi_experiment/bash/download-pinciroli-results.sh`.
To generate the figures etc., run the different Python notebooks.
If you don't want to go through the process of installing e.g., Jupyter, you can simply run [this script](./gssi_experiment/bash/run-notebooks-as-python.sh) as well, which runs all of the notebooks experiments as regular Python scripts.
After doing this, all of the figures can be found in the patterns' respective `figures` folder.
If you used the script, the logs (in which correlation, etc. are printed), can be found in the notebooks' respective `.out` files.

## The gateway aggregator

This study implemented a custom gateway aggregator service, which can be found [here](./gssi_experiment/gateway_aggregator/gateway_aggregator_service) and has a corresponding [docker.io repository](https://hub.docker.com/layers/wmeijer221/microservice_v4-screen/gateway_aggregator/images/sha256-38e9923fea35aff272d1cfb0c1df8c714b9afca907a02b6cf7fccc9445e222db?context=repo).
It is built using [FastAPI](https://fastapi.tiangolo.com/), which is picked for no particular reason beyond its simplicity.
Services can make aggregate API requests using the `/api/v1` endpoint, which is chosen because this is the default in muBench.
It implements a very primitive version of a gateway aggregator using request headers to infer the aggregated requests.
It has two modes of operation: parallel and sequential, defining how the requests are executed (the experiment exclusively uses parallel execution).
To efficiently forward requests, it identifies whether a local pod of the queried service exists, and forwards it directly to that in case one is present.
Otherwise, aggregate requests are simply forwarded through the ingress.

## Changes to muBench

It should be noted that this repository is a fork of [that of Detti et al.](https://github.com/mSvcBench/muBench), who developed muBench.
The version found here alters their source code to support the purposes of the study.
Specifically, it implements the following features:

- Custom header propagation in the `ServiceCell`
- Internal and external load selection based on request headers.
  - In the `WorkModel` simply set `request_type_dependent_internal_service` or `request_type_dependent_external_service` to true, and then add dictionary entries for each request type in the `external_service` or `internal_service` (see services `s1` and `s2` in [this work model](./pipes_and_filters/pipes_and_filters_joint/WorkModel.json) for examples of this).
  - (To use this, you need to configure the header types in the `RunnerParameters`; see the next point.)
- Added a request header factory to `Runner`, which is implemented [here](../Benchmarks/Runner/QueryStringBuilder.py).
  - To use this, simply add `HeaderParameters` to your `RunnerParameters.json` (see [this config file](./gateway_aggregator/RunnerParameters.json) for an example.)
- Added option to include custom services into the system's topology by adding an edge-case in the `K8sYamlDeployer`.
  - To include a custom service in the topology, simply add its entry in the respective `WorkModel` and set `is_generated` to false (see [this work model](./gateway_aggregator/WorkModel.json) for an example). The service does have to be deployed into Kubernetes manually, though.
- Made a bunch of work model entries optional in the `ServiceCell` to remove a lot of boilerplate configuration fields.
- You can reference your own template file folder; i.e., the system isn't hard-coded to use `./Deployers/K8sDeployer/Templates/`.
  - To specify a new path, run the `K8sDeployer.py` with the `-ybp` command line parameter set with the to-be-used path.
- Probably some other minor things that I can't remember.
