# Overview GSSI Experiment Performance Design Patterns

## Contents

- [Trial Experiment](./trial_experiment/): Contains all files necessary to run one of the default `muBench` simulations.
- [Gateway Aggregator](./gateway_aggregator/): Experiment files for the gateway aggregator.
- [Pipes and Filters](./pipes_and_filters/): idem.
- [Gateway Offloading](./gateway_offloading): idem.
- [Base](./base.py): Contains all common functions used by the underlying experiments.

## Experimental Design

### Gateway Aggregator

### Pipes and Filters

### Gateway Offloading

## TODO:

### General

- [x] Add easy to change deployment restrictions.

### Gateway aggregator

- [x] Implement gateway aggregator service.
- [x] Add support for non-synthetic service definitions in `muBench` `WorkModels`.
- [x] Add support for request type-based service load in `muBench` `ServiceCell`.
- [x] Add support for custom headers in `muBench` `Runner`.
- [x] Set up gateway aggregator pattern experiment using `muBench`.

### Gateway offloading

- [x] Implement header-based forwarding (i.e., a header specifies the endpoint, not the probability) in `muBench` `ServiceCell`.
- [] Set up gateway offloading pattern without offloading using `muBench`.
- [] Set up gateway offloading pattern with minor offloading using `muBench`.
- [] Set up gateway offloading pattern with major offloading using `muBench`.

### Pipes and filters

- [] Implement header-based forwarding in the `ServiceCell` component. This is necessary for the pipes and filters experiment.
- [] Set up pipes and filters pattern for the separated experiment using `muBench`.
- [] Set up pipes and filters pattern for the joint (x1) experiment using `muBench`.
- [] Set up pipes and filters pattern for the joint (x2) experiment using `muBench`.

## Installation Guide and Experimental Setup

As the experiment is ran on a real cluster, the installation guide is not completely trivial.
Two main technologies are used to set up a kubernetes cluster: OpenStack and [k3s](https://docs.k3s.io/quick-start).
Of these, only k3s needed to be set up in this study as the OpenStack environment was directly available.
Simply put, k3s is an easy-to-use variant of kubernetes that preselects things such as the network controller, designed for small scale clusters and edge devices.

This experiment defined three large compute nodes running `Ubuntu-22.04-x86_64-2022-11-13`.
When doing this, there are a number of things to consider: 1) setting up a key pair allow access through SSH, 2) configuring the system's firewall to allow ingress data on ports 22 (ssh), 6443 (kubectl), and 31113 (for the deployed apps in this experiment), and 3) defining a number of floating IPs to grant access to the different nodes from your local device.
After you have set up a number of compute nodes in your OpenStack environment, you can install k3s by simply following the instructions on their quick-start page (you can easily do this by SSH-ing into the different nodes).

Then, to connect to the cluster from your local device, copy the config file of the master node (stored in `/etc/rancher/k3s/k3s.yaml`) on your local device (as `~/.kube/config`).
On your local device, change the IP address of the server to one of the floating IP you created in OpenStack.
You should be able to run commands like `kubectl get nodes` now.

To set up the monitoring tools issues by `muBench`, simply follow the instructions in the [manual](../Docs/Manual.md#install-and-access-the-monitoring-framework), which can be summarized to run: `./Monitoring/kubernetes-full-monitoring/monitoring-install.sh`.
This enables Prometheus, Kiali, and Jaeger.
Note that to gain access to the tools' web clients, ports `30001:30003` should be opened up in OpenStack `Security Group` rules that apply to your master node.

To run any of the experiments, run any of the Python file in the `gssi_experiment` folder. For example `python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py`, which will run the gateway aggregator experiments using default variables.

_Note: because nginx can't resolve docker hostnames (e.g., `service-1.default.svc.cluster.local`), the resolver fields in `./Deployers/K8sDeployer/Templates/ConfigMapNginxGwTemplate.yaml` reference a static IP. Odds are that this IP will change when the cluster is deployed (this issue somehow does not exist in `minikube`). Therefore, make sure to update both resolver fields in this file to the IP address corresponding to the `kube-dns` service. There are better ways to solve this issue, but this was the easiest one for the sake of this experiment._

Although the experiments can be ran using any device, re-running the experiments this way would likely introduce noise in the measured request delay due to potentially network issues on the device's network.
Therefore, a fourth node is launched in the OpenStack environment, which is not configured to join the kubernetes cluster, and experiments are ran using this device. A consequence of this is that the measured delay might be notably lower than in real-life scenarios, however, this should not affect the measured outcomes as network delays more-or-less only add a constant to the total (and some noise).
