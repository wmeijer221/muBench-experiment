#! /bin/bash

curl -X POST http://gateway-aggregator.default.svc.cluster.local:80/ratio/ \
    -H "Content-Type: application/json" \
    -d '{"ratio": 0.5}'

curl -X POST http://gateway-aggregator.default.svc.cluster.local:80/targets/ \
    -H "Content-Type: application/json" \
    -d '{"service_1": "http://s1.default.svc.cluster.local:80/api/v1", "service_2": "http://s2.default.svc.cluster.local:80/api/v1", "service_3": "http://s3.default.svc.cluster.local:80/api/v1"}'

curl -X GET http://gateway-aggregator.default.svc.cluster.local:80/
