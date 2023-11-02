
# Gateway Aggregator Service

Implements a simple gateway aggregator pattern as described by [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/patterns/gateway-aggregation).

The implementation accounts for a number of implementation considerations:
- Parallel vs. sequential API calls.
- Partial data return on a failed API call.
