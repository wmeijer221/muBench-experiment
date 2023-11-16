# Configurations of big experiment #1: workload=15000, trials=25 (effectively randomly chosen).
# Configurations of big experiment #2: workload=10000, trials=17 (chosen and reduce time to emphasize vCPU=1, respectively).

LOGS_PATH=./gssi_experiment/gateway_offloading/results/small_experiment_1/logs.out
mkdir -p ./gssi_experiment/gateway_offloading/results/small_experiment_1
echo > ./gssi_experiment/gateway_offloading/results/small_experiment_1/logs.out

# {


DELAY=15
BIG_NODE=node-3
SMALL_NODE_1=node-1
SMALL_NODE_2=node-2
WORKLOAD=20000
# This is 17 because at trials=25 the most accurate model lay at vCPU limit=1500m
# i.e., if we want to model for 1 vCPU, the load should be reduced by 1/3; i.e. to trials~17.
TRIALS=10
STEPS=5

let counter=1000

RERUNS=3

for VARIABLE in 1 ... $RERUNS
do
    python3 ./gssi_experiment/gateway_offloading/service_intensity_gwo_experiment.py \
        --wait-for-pods $DELAY \
        --seed $counter \
        --steps $STEPS \
        --trials $TRIALS \
        --gateway-load [0,10,2] \
        --workload-events $WORKLOAD \
        --node-selector $BIG_NODE,minikube \
        --replicas 1 \
        --cpu-limit 1000m \
        --name "small_experiment_1/1000m_1rep_17trials/run_$VARIABLE"
    let counter++

done

# } | tee -a $LOGS_PATH
