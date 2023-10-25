# Experimental Setup 

This folder contains some experimental results that specifically address the effects of used threads. Here, each of the experiments are performed using the CPU load analogous to Pinciroli's work, amplified to execute 15 trials. 

The first nuber in the figure name represents the number of threads used. This means that in the ``WorkModel.json`` all fields ``thread_pool_size`` and ``workers`` are set to that number.
The ``threads`` field is set to the same number for the experiments using 12 and 14 threads, and set to 32 for the 16 thread experiments.

Additionally, ``thread_pool_size`` in the ``RunnerParameters`` is set to this number as well.

Any additional changes are marked in the figure name.

A small-scale experiment is performed, using 400 requests and only 4 different values of ``s1_intensity``.

# Experimental Environment

Ran on a single commodity device using minikube.

# Findings

The U curve shown in Pinciroli's work is not nearly as present in any of the experiments here.
Arguably, a slight curve can be observed in the average response time curve, however, is nowhere near as obvious as in Pinciroli's work. 
Interestingly, the minimum response time seems to follow this curve quite consistently, albeit very mildly as well.

# Conclusions

I am fairly certain the results generated in Pinciroli's work cannot be replicated on a single machine. Consequently, I am fairly certain that their results are wholly dependent on the fact that single services bottleneck - i.e., that each service has a separate compute node. - which is unrealistic in microservice architectures.

Pod resources can be restricted in Kubernetes, which is a reasonable next step to explore.
