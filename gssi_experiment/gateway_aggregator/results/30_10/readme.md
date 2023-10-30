# Experimental Setup

Continuation of the results generated on October 25th, in order to verify the observed patterns.

Here, each service is limited to `1000m`; i.e., one CPU.
The tests are performed using 5 different values of `s1 sensitivity` and 1000 requests (the experiments of the 25th used 4000 requests, which minimizes noise).
The performance load is analagous to that of pincirolli's.

## Experimental variant 1: Increased resources

**Note:** The scalability of this experiment is limited to the size of the commodity device. e.g., `4000m` could not be tested.

### Variant A: 2000m

In this experiment, the resources accessible to each service are increased to `2000m`; i.e., 2 CPUs.

When observing the generated charts, it stands out immediately, that the U shape is more prominent here, and that the delay is substantially lower. Interestingly, although the U shape is more prominent, fully S1 and S3 intense loads have lower delays than largely S1 and S3 intensive loads. Running this exact experiment again, with 2000 requests, does not yield this result, suggesting it's simply noise.

### Variant B: No limit

This is effectively the same experiment as before, however, no CPU limit is specified in this scenario.
In this scenario, more or less the same observations can be made as in the 2 CPU scenario. The delays are noticeably lower than before, and in this scenario, a U shape can be observed as well.

Interestingly, the second run does not show an U shape. As at `s1_intensity=0.4`, a large spike can be seen. Which moved to `s1_intensity=0.6` in the third iteration of this experiment.

It should be noted that CPU throttling never occurred during these experiments. This is imiportant, as Pincorilli's results do report this. Although CPU throttling is not measured in the limited resource experiments, it most likely occurred as CPU usage is much, much higher in the no-limit scenario, and they are tested with the same type of load.

### Variant C: 3000m

Same experiment but with 3 CPUs. You can see the same results as with 2000m. The overall delay is much lower, and there is a U curve present.

### Variant D: 1000m with 3 replicas.

A similar phenomenon occurs here compared to the no limit experiments: although the first experiment showed some U-shape behaviour, the second did not completely as at `s1_intensity=0.6` the delay suddenly peaks again. The third experiment, however, more or less follows the expected distribution again. Note that the third experiment used 8 `s1_intensity` points and 4000 requests per simulation.

### Conclusions

Contrary to what was initially expected, the theoretical model is most likely consistent for services with more resources than 1 CPU. Albeit slightly noisy the different experiments consistently followed the hypothesized U-curve. Some emphasis should be put on "albeit noisy", though, during the "common saturation sector" some unexplained behaviour is present (where the delay suddenly spikes for a given `s1_intensity` value, however, occurs inconsistently). This is most likely false behaviour, only present because the measurements are performed on a commodity machine, but should be re-evaluated in the "real" experimental environment.

## Experimental variant 2: Increased loads.

# experimental setup

Commodity machine.

# Conclusions

The baseline results show a more or less similar U shape, albeit with some noise around the curve's expected peak.
