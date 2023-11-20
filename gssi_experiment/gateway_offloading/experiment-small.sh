#! /bin/bash

BASE_PATH=./gssi_experiment/gateway_offloading/results/small_experiment_3
LOGS_PATH=$BASE_PATH/logs.out
mkdir -p $BASE_PATH
echo > $LOGS_PATH

DELAY=60
BIG_NODE=node-3
SMALL_NODE_1=node-1
SMALL_NODE_2=node-2

STEPS=5

let counter=1000

python3 ./gssi_experiment/gateway_offloading/experiment_runner_wrapper.py \
    --wait-for-pods $DELAY \
    --node-selector $BIG_NODE,minikube \
    --steps $STEPS \
    --seed $counter \
    --replicas 1 \
    --cpu-limit 1000m \
    --gateway-load "[0,10,1]" \
    --name "small_experiment_2/1000m_1rep_17trials/run_1"
let counter++
