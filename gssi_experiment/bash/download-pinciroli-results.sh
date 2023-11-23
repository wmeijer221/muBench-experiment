#! /bin/bash

# Downloads the synthetic results created by Pinciroli et al. (2023) used to compare this work with.

curl https://raw.githubusercontent.com/rickypinci/performance-models-cdp/main/Gateway_Aggregation/multi_N25.csv > ./gssi_experiment/gateway_aggregator/multi_N25.csv

curl https://raw.githubusercontent.com/rickypinci/performance-models-cdp/main/Gateway_Offloading/multi_N25.csv > ./gssi_experiment/gateway_offloading/multi_N25.csv

curl https://raw.githubusercontent.com/rickypinci/performance-models-cdp/main/Pipes_and_Filters/joint/Core1_N50.csv > ./gssi_experiment/pipes_and_filters/pipes_and_filters_joint/Core1_N50.csv

curl https://raw.githubusercontent.com/rickypinci/performance-models-cdp/main/Pipes_and_Filters/joint/Core2_N50.csv > ./gssi_experiment/pipes_and_filters/pipes_and_filters_joint/Core2_N50.csv

curl https://raw.githubusercontent.com/rickypinci/performance-models-cdp/main/Pipes_and_Filters/separated/Core1_N50.csv > ./gssi_experiment/pipes_and_filters/pipes_and_filters_separated/Core1_N50.csv
