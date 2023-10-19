#! /bin/bash

# Example: ``./gssi_experiment/run-full-experiment.sh ./gssi_experiment/trial_experiment/K8sParameters.json ./gssi_experiment/trial_experiment/RunnerParameters.json``

echo Running experiment with topology: \"$1\"
python3 Deployers/K8sDeployer/RunK8sDeployer.py -c $1 -cl -y
