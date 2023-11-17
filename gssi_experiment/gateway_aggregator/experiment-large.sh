# Configurations of big experiment #1: workload=15000, trials=25 (effectively randomly chosen).
# Configurations of big experiment #2: workload=10000, trials=17 (chosen and reduce time to emphasize vCPU=1, respectively).

BASE_PATH=./gssi_experiment/gateway_aggregator/results/large_experiment_3
LOGS_PATH=$BASE_PATH/logs.out
mkdir -p $BASE_PATH
echo > $BASE_PATH/logs.out


DELAY=60
BIG_NODE=node-3
SMALL_NODE_1=node-1
SMALL_NODE_2=node-2
TRIALS=10
STEPS=5

let counter=1

VARIABLE=1


python3 ./gssi_experiment/gateway_aggregator/experiment_runner_wrapper.py \
    --wait-for-pods $DELAY \
    --node-selector $BIG_NODE,minikube \
    --steps $STEPS \
    --seed $counter \
    --cpu-limit 1000m \
    --replicas 1 \
    --name "large_experiment_3/1000m_1rep_10trials/run_$VARIABLE"
let counter++

# This experiment is placed at the bottom because it's very slow.
python3 ./gssi_experiment/gateway_aggregator/experiment_runner_wrapper.py \
    --wait-for-pods $DELAY \
    --node-selector $BIG_NODE,minikube \
    --steps $STEPS \
    --seed $counter \
    --cpu-limit 500m \
    --replicas 1 \
    --name "large_experiment_3/500m_1rep_10trials/run_$VARIABLE"
let counter++

python3 ./gssi_experiment/gateway_aggregator/experiment_runner_wrapper.py \
    --wait-for-pods $DELAY \
    --node-selector $BIG_NODE,minikube \
    --steps $STEPS \
    --seed $counter \
    --cpu-limit 1500m \
    --replicas 1 \
    --name "large_experiment_3/1500m_1rep_10trials/run_$VARIABLE"
let counter++

python3 ./gssi_experiment/gateway_aggregator/experiment_runner_wrapper.py \
    --wait-for-pods $DELAY \
    --node-selector $BIG_NODE,minikube \
    --steps $STEPS \
    --seed $counter \
    --cpu-limit 2000m \
    --replicas 1 \
    --name "large_experiment_3/2000m_1rep_10trials/run_$VARIABLE"
let counter++

python3 ./gssi_experiment/gateway_aggregator/experiment_runner_wrapper.py \
    --wait-for-pods $DELAY \
    --node-selector $BIG_NODE,minikube \
    --steps $STEPS \
    --seed $counter \
    --cpu-limit 2500m \
    --replicas 1 \
    --name "large_experiment_3/2500m_1rep_10trials/run_$VARIABLE"
let counter++

python3 ./gssi_experiment/gateway_aggregator/experiment_runner_wrapper.py \
    --wait-for-pods $DELAY \
    --node-selector $BIG_NODE,minikube \
    --steps $STEPS \
    --seed $counter \
    --cpu-limit '' \
    --replicas 1 \
    --name "large_experiment_3/no_cpu_cap_1rep_10trials/run_$VARIABLE"
let counter++

python3 ./gssi_experiment/gateway_aggregator/experiment_runner_wrapper.py \
    --wait-for-pods $DELAY \
    --node-selector $BIG_NODE,$SMALL_NODE_1,minikube \
    --steps $STEPS \
    --seed $counter \
    --cpu-limit 1000m \
    --replicas 2 \
    --name "large_experiment_3/1000m_2rep_10trials/run_$VARIABLE"
let counter++

python3 ./gssi_experiment/gateway_aggregator/experiment_runner_wrapper.py \
    --wait-for-pods $DELAY \
    --node-selector $BIG_NODE,$SMALL_NODE_1,$SMALL_NODE_2,minikube \
    --steps $STEPS \
    --seed $counter \
    --cpu-limit 1000m \
    --replicas 3 \
    --name "large_experiment_3/1000m_3rep_10trials/run_$VARIABLE"
let counter++

python3 ./gssi_experiment/gateway_aggregator/experiment_runner_wrapper.py \
    --wait-for-pods $DELAY \
    --node-selector $BIG_NODE,$SMALL_NODE_1,$SMALL_NODE_2,minikube \
    --steps $STEPS \
    --seed $counter \
    --cpu-limit '' \
    --replicas 3 \
    --name "large_experiment_3/no_cpu_cap_3rep_10trials/run_$VARIABLE"
let counter++

