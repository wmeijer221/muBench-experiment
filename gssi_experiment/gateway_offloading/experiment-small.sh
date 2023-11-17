#! /bin/bash

BASE_PATH=./gssi_experiment/gateway_offloading/results/small_experiment_2
LOGS_PATH=$BASE_PATH/logs.out
mkdir -p $BASE_PATH
echo > $LOGS_PATH

{


DELAY=15
BIG_NODE=node-3
SMALL_NODE_1=node-1
SMALL_NODE_2=node-2

TRIALS=500
STEPS=5

let counter=1000

for VARIABLE in {1..3}
do
    python3 ./gssi_experiment/gateway_offloading/service_intensity_gwo_experiment.py \
        --wait-for-pods $DELAY \
        --seed $counter \
        --steps $STEPS \
        --trials $TRIALS \
        --gateway-load [0,10,2] \
        --node-selector $BIG_NODE,minikube \
        --replicas 1 \
        --cpu-limit 1000m \
        --name "small_experiment_2/1000m_1rep_17trials/run_$VARIABLE"
    let counter++

done

} | tee -a $LOGS_PATH
