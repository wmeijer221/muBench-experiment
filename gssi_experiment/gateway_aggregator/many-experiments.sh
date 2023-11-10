DELAY=5
BIG_NODE=node-3


for VARIABLE in 1 2 3
do
    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials 25 \
        --seed 1 \
        --workload-events 15000 \
        --cpu-limit 1000m \
        --replicas 1 \
        --name "1000m_1rep_25trials/run_$VARIABLE"

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials 25 \
        --seed 2 \
        --workload-events 15000 \
        --cpu-limit 750m \
        --replicas 1 \
        --name "750m_1rep_25trials/run_$VARIABLE"

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials 25 \
        --seed 3 \
        --workload-events 15000 \
        --cpu-limit 1250m \
        --replicas 1 \
        --name "1250m_1rep_25trials/run_$VARIABLE"

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials 25 \
        --seed 4 \
        --workload-events 15000 \
        --cpu-limit 500m \
        --replicas 1 \
        --name "500m_1rep_25trials/run_$VARIABLE"

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials 25 \
        --seed 5 \
        --workload-events 15000 \
        --cpu-limit 1500m \
        --replicas 1 \
        --name "1500m_1rep_25trials/run_$VARIABLE"

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials 25 \
        --seed 6 \
        --workload-events 15000 \
        --cpu-limit 1750m \
        --replicas 1 \
        --name "1750m_1rep_25trials/run_$VARIABLE"

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials 25 \
        --seed 7 \
        --workload-events 15000 \
        --cpu-limit 2000m \
        --replicas 1 \
        --name "2000m_1rep_25trials/run_$VARIABLE"

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials 25 \
        --seed 8 \
        --workload-events 15000 \
        --cpu-limit 2500m \
        --replicas 1 \
        --name "2500m_1rep_25trials/run_$VARIABLE"

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method node_selector \
        --steps 25 \
        --trials 25 \
        --seed 9 \
        --workload-events 15000 \
        --cpu-limit '' \
        --replicas 1 \
        --name "no_cpu_cap_1rep_25trials/run_$VARIABLE"

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method equal_distribution \
        --steps 25 \
        --trials 25 \
        --seed 10 \
        --workload-events 15000 \
        --cpu-limit 1000m \
        --replicas 2 \
        --name "1000m_2rep_25trials/run_$VARIABLE"

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method equal_distribution \
        --steps 25 \
        --trials 25 \
        --seed 11 \
        --workload-events 15000 \
        --cpu-limit 1000m \
        --replicas 3 \
        --name "1000m_3rep_25trials/run_$VARIABLE"

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method equal_distribution \
        --steps 25 \
        --trials 25 \
        --seed 10 \
        --workload-events 15000 \
        --cpu-limit '' \
        --replicas 2 \
        --name "no_cpu_cap_2rep_25trials/run_$VARIABLE"

    python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
        --wait-for-pods $DELAY \
        --node-selector $BIG_NODE \
        --node-selector-method equal_distribution \
        --steps 25 \
        --trials 25 \
        --seed 11 \
        --workload-events 15000 \
        --cpu-limit '' \
        --replicas 3 \
        --name "no_cpu_cap_3rep_25trials/run_$VARIABLE"
done

