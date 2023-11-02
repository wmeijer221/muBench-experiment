# Overview GSSI Experiment Performance Design Patterns

## Contents

- [Trial Experiment](./trial_experiment/): Contains all files necessary to run one of the default `muBench` simulations.
- [Gateway Aggregator](./gateway_aggregator/): Experiment files for the gateway aggregator.
- [Pipes and Filters](./pipes_and_filters/): idem.
- [Gateway Offloading](./gateway_offloading): idem.
- [Base](./base.py): Contains all common functions used by the underlying experiments.

## Experimental Design

### Gateway Aggregator

### Pipes and Filters

### Gateway Offloading

## TODO:

### Gateway aggregator

- [x] Implement gateway aggregator service.
- [x] Add support for non-synthetic service definitions in `muBench` `WorkModels`.
- [x] Add support for request type-based service load in `muBench` `ServiceCell`.
- [x] Add support for custom headers in `muBench` `Runner`.
- [x] Set up gateway aggregator pattern experiment using `muBench`.

### Gateway offloading

- [] Set up gateway offloading pattern without offloading using `muBench`.
- [] Set up gateway offloading pattern with minor offloading using `muBench`.
- [] Set up gateway offloading pattern with major offloading using `muBench`.

### Pipes and filters

- [] Implement header-based forwarding in the `ServiceCell` component. This is necessary for the pipes and filters experiment.
- [] Set up pipes and filters pattern for the separated experiment using `muBench`.
- [] Set up pipes and filters pattern for the joint (x1) experiment using `muBench`.
- [] Set up pipes and filters pattern for the joint (x2) experiment using `muBench`.
