#! /bin/bash

# Runs the python notebooks as regular python files, so you can generate
# results etc. without having to install e.g. jupyter. All logs are stored
# in the notebook's folders in .out files.

RUNNER=./gssi_experiment/util/run_python_notebook.py

python3 $RUNNER ./gssi_experiment/gateway_aggregator/analysis_singular.ipynb
python3 $RUNNER ./gssi_experiment/gateway_offloading/analysis_singular.ipynb
python3 $RUNNER ./gssi_experiment/pipes_and_filters/pipes_and_filters_joint/analysis_singular_1cpu.ipynb
python3 $RUNNER ./gssi_experiment/pipes_and_filters/pipes_and_filters_joint/analysis_singular_2cpu.ipynb
python3 $RUNNER ./gssi_experiment/pipes_and_filters/pipes_and_filters_separated/analysis_singular.ipynb
