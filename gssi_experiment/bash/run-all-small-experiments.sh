#! /bin/bash

SLEEP_TIME=120

./gssi_experiment/pipes_and_filters/pipes_and_filters_joint/experiment-small.sh
sleep $SLEEP_TIME

./gssi_experiment/pipes_and_filters/pipes_and_filters_separated/experiment-small.sh
sleep $SLEEP_TIME

./gssi_experiment/gateway_offloading/experiment-small.sh
sleep $SLEEP_TIME

# This should probably not be run before the others as the
# aggregator service isn't automatically deleted yet.
./gssi_experiment/gateway_aggregator/experiment-small.sh
sleep $SLEEP_TIME
