python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
    -w 60 \
    --node-selector node-2 \
    -s 20 \
    --trials 5
mv ./SimulationWorkspace/Result/result.txt ./SimulationWorkspace/Result/result_5_trials.txt
mv ./gssi_experiment/gateway_aggregator/results/figure_stitched.png gssi_experiment/gateway_aggregator/results/figure_stitched_5_trials.png

python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
    -w 60 \
    --node-selector node-2 \
    -s 20 \
    --trials 10
mv ./SimulationWorkspace/Result/result.txt ./SimulationWorkspace/Result/result_10_trials.txt
mv ./gssi_experiment/gateway_aggregator/results/figure_stitched.png gssi_experiment/gateway_aggregator/results/figure_stitched_10_trials.png

python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
    -w 60 \
    --node-selector node-2 \
    -s 20 \
    --trials 15
mv ./SimulationWorkspace/Result/result.txt ./SimulationWorkspace/Result/result_15_trials.txt
mv ./gssi_experiment/gateway_aggregator/results/figure_stitched.png gssi_experiment/gateway_aggregator/results/figure_stitched_15_trials.png

python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
    -w 60 \
    --node-selector node-2 \
    -s 20 \
    --trials 20
mv ./SimulationWorkspace/Result/result.txt ./SimulationWorkspace/Result/result_20_trials.txt
mv ./gssi_experiment/gateway_aggregator/results/figure_stitched.png gssi_experiment/gateway_aggregator/results/figure_stitched_20_trials.png

python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
    -w 60 \
    --node-selector node-2 \
    -s 20 \
    --trials 25
mv ./SimulationWorkspace/Result/result.txt ./SimulationWorkspace/Result/result_25_trials.txt
mv ./gssi_experiment/gateway_aggregator/results/figure_stitched.png gssi_experiment/gateway_aggregator/results/figure_stitched_25_trials.png

python3 ./gssi_experiment/gateway_aggregator/service-intensity-experiment.py \
    -w 60 \
    --node-selector node-2 \
    -s 20 \
    --trials 30
mv ./SimulationWorkspace/Result/result.txt ./SimulationWorkspace/Result/result_30_trials.txt
mv ./gssi_experiment/gateway_aggregator/results/figure_stitched.png gssi_experiment/gateway_aggregator/results/figure_stitched_30_trials.png
