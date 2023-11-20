#! /bin/bash

BASE_PATH=./gssi_experiment/pipes_and_filters/pipes_and_filters_joint/results/experiment_small_3

LOGS_PATH=$BASE_PATH/logs.out
mkdir -p $BASE_PATH
echo > $BASE_PATH/logs.out


DELAY=60
BIG_NODE=node-3
SMALL_NODE_1=node-1
SMALL_NODE_2=node-2

STEPS=5

VARIABLE=1

let counter=2000

python3 ./gssi_experiment/pipes_and_filters/pipes_and_filters_joint/experiment_runner_wrapper.py \
    --wait-for-pods $DELAY \
    --node-selector minikube \
    --steps $STEPS \
    --seed $counter \
    --cpu-limit 1000m \
    --replicas 1 \
    --name "experiment_small_3/1000m_1rep_17trials/run_$VARIABLE"
let counter++

