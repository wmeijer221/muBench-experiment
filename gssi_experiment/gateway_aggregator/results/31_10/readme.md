# Experimental setup

Goals:

- Evaluate the impact of sequential execution of calls.
- Visualize the delay in S3 and S1 type requests.
- Evaluate the impact of large in-memory joins.

## Experimental variant 1: sequential execution

This experiment compares whether sequential execution of requests in the gateway aggregator affects the representativeness of the theoretical model. The experiment sets the header field `x-aggregatesequentially` to `true` or `false` and tests its impact.

When observing the figures, there is a clear difference between sequential and parallel execution, such that parallel execution does follow the expected U curve, and sequential execution does not. This makes sense as the there is not transition in what service saturates in the sequential model, the bottleneck doesn't transition from one service to another, instead, they are added to each other.

## Experimental variant 2: visualize delay S1 and S3 requesttypes.

Executed with CPU load analogous to Pincirolli's, multiplied by `trials=20`.
The experiment is ran with 4000 requests, where each service is limited to `2000m` (i.e., 2 CPUs), without any replicas.

You can see that S1 request delay increases as S1 intensity increases.
S3 requests have a similar effect, but in a much different manner; the delay is very high for very high S3 intensities, but remains stable afterwards.

As expected, the complete picture is more or less a combination of the two.

It stands out that during the second iteration of the experiment, S1 delays start very high as well; i.e., with few S1 requests, the delay is very high; this wholly contradicts expectations and the previous results. In this scenario, however, the S3 request charts show an linear-like decrease in delay as they become less frequent, which was not as present in during the previous experiment.

## Experimental variant 3: large in-memory joins
