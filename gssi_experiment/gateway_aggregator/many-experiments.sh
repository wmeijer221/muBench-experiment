# Configurations of big experiment #1: workload=15000, trials=25 (effectively randomly chosen).
# Configurations of big experiment #2: workload=10000, trials=17 (chosen and reduce time to emphasize vCPU=1, respectively).


DELAY=60
BIG_NODE=node-3
WORKLOAD=10000
# This is 17 because at trials=25 the most accurate model lay at vCPU limit=1500m
# i.e., if we want to model for 1 vCPU, the load should be reduced by 1/3; i.e. to trials~17.
TRIALS=17

let counter=1

for VARIABLE in 1 2 3
do
    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials $TRIALS \
        --seed $counter \
        --workload-events $WORKLOAD \
        --cpu-limit 1000m \
        --replicas 1 \
        --name "large_experiment_2/1000m_1rep_20trials/run_$VARIABLE"
    let counter++

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials $TRIALS \
        --seed $counter \
        --workload-events $WORKLOAD \
        --cpu-limit 750m \
        --replicas 1 \
        --name "large_experiment_2/750m_1rep_20trials/run_$VARIABLE"
    let counter++

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials $TRIALS \
        --seed $counter \
        --workload-events $WORKLOAD \
        --cpu-limit 1250m \
        --replicas 1 \
        --name "large_experiment_2/1250m_1rep_20trials/run_$VARIABLE"
    let counter++

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials $TRIALS \
        --seed $counter \
        --workload-events $WORKLOAD \
        --cpu-limit 500m \
        --replicas 1 \
        --name "large_experiment_2/500m_1rep_20trials/run_$VARIABLE"
    let counter++

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials $TRIALS \
        --seed $counter \
        --workload-events $WORKLOAD \
        --cpu-limit 1500m \
        --replicas 1 \
        --name "large_experiment_2/1500m_1rep_20trials/run_$VARIABLE"
    let counter++

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials $TRIALS \
        --seed $counter \
        --workload-events $WORKLOAD \
        --cpu-limit 1750m \
        --replicas 1 \
        --name "large_experiment_2/1750m_1rep_20trials/run_$VARIABLE"
    let counter++

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials $TRIALS \
        --seed $counter \
        --workload-events $WORKLOAD \
        --cpu-limit 2000m \
        --replicas 1 \
        --name "large_experiment_2/2000m_1rep_20trials/run_$VARIABLE"
    let counter++

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials $TRIALS \
        --seed $counter \
        --workload-events $WORKLOAD \
        --cpu-limit 2500m \
        --replicas 1 \
        --name "large_experiment_2/2500m_1rep_20trials/run_$VARIABLE"
    let counter++

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials $TRIALS \
        --seed $counter \
        --workload-events $WORKLOAD \
        --cpu-limit '' \
        --replicas 1 \
        --name "large_experiment_2/no_cpu_cap_1rep_20trials/run_$VARIABLE"
    let counter++

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method equal_distribution \
        --steps 25 \
        --trials $TRIALS \
        --seed $counter \
        --workload-events $WORKLOAD \
        --cpu-limit 1000m \
        --replicas 2 \
        --name "large_experiment_2/1000m_2rep_20trials/run_$VARIABLE"
    let counter++

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method equal_distribution \
        --steps 25 \
        --trials $TRIALS \
        --seed $counter \
        --workload-events $WORKLOAD \
        --cpu-limit 1000m \
        --replicas 3 \
        --name "large_experiment_2/1000m_3rep_20trials/run_$VARIABLE"
    let counter++

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method equal_distribution \
        --steps 25 \
        --trials $TRIALS \
        --seed $counter \
        --workload-events $WORKLOAD \
        --cpu-limit '' \
        --replicas 2 \
        --name "large_experiment_2/no_cpu_cap_2rep_20trials/run_$VARIABLE"
    let counter++

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method equal_distribution \
        --steps 25 \
        --trials $TRIALS \
        --seed $counter \
        --workload-events $WORKLOAD \
        --cpu-limit '' \
        --replicas 3 \
        --name "large_experiment_2/no_cpu_cap_3rep_20trials/run_$VARIABLE"
    let counter++

done

