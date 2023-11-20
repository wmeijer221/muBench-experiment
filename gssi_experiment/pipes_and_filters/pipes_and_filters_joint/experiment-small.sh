#! /bin/bash

EXP_NAME=pinciroli_replication_1
BASE_PATH=./gssi_experiment/pipes_and_filters/pipes_and_filters_joint/results/$EXP_NAME

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
    --node-selector $BIG_NODE,minikube \
    --steps $STEPS \
    --seed $counter \
    --cpu-limit 1000m \
    --replicas 1 \
    --name $EXP_NAME/experiment_$counter
let counter++

python3 ./gssi_experiment/pipes_and_filters/pipes_and_filters_joint/experiment_runner_wrapper.py \
    --wait-for-pods $DELAY \
    --node-selector $BIG_NODE,minikube \
    --steps $STEPS \
    --seed $counter \
    --only-shared-cpu-limits \
    --cpu-limit 2000m \
    --replicas 1 \
    --name $EXP_NAME/experiment_$counter
let counter++

