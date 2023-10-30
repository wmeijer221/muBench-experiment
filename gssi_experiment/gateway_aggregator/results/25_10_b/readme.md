# Experimental setup

Tests the impact of limiting mubench services on the amount of CPU they have.
Each of these services is limited to `1000m` CPUs (i.e. 1 CPU).

The main idea for this experiment is the assumption that Pinciroli's results are dependent on the fact that each service throttles separately. This is not possible to measure in a one-node cluster where no restrictions are applied as services only throttle when all of them do. Virtually restricting services might be able to trigger CPU throttling.

Note that both the `mubench-ingress` and `gateway-aggregator` are not limited in any fashion. This is because limiting either would just increase the delay by a constant and likely make it more difficult to measure throttling in the microservices.

Then, different loads are tested.
The CPU stress is still analogous compared to Pinciroli's work, however, amplified to a lesser extent to reflect the reduction in CPU access the services have.

By default, they are executed with a `thread_pool_size` of 1, using 4 `workers` and `8` threads.

A small-scale experiment is performed, using 400 requests and only 4 different values of ``s1_intensity``.

# Experimental environment

Still the single commodity machine and minikube.

# Results

The curve shape shown for 5 and 30 trials is non-linear, however, does not represent a clear U shape still.
The same applies for the experiment using more threads.