#! /bin/bash

SLEEP_TIME=120

chmod +x gssi_experiment/pipes_and_filters/pipes_and_filters_joint/experiment-small.sh
./gssi_experiment/pipes_and_filters/pipes_and_filters_joint/experiment-small.sh
sleep $SLEEP_TIME

chmod +x gssi_experiment/pipes_and_filters/pipes_and_filters_separated/experiment-small.sh
./gssi_experiment/pipes_and_filters/pipes_and_filters_separated/experiment-small.sh
sleep $SLEEP_TIME

chmod +x gssi_experiment/gateway_offloading/experiment-small.sh
./gssi_experiment/gateway_offloading/experiment-small.sh
sleep $SLEEP_TIME

# This should probably not be run before the others as the
# aggregator service isn't automatically deleted yet.
chmod +x gssi_experiment/gateway_aggregator/experiment-small.sh
./gssi_experiment/gateway_aggregator/experiment-small.sh
sleep $SLEEP_TIME
