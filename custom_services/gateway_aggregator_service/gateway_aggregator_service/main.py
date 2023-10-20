"""
Implements simple gateway aggregator.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import aggregator
import models


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://0.0.0.0:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


S1_RATIO = 1
SERVICE_1 = ""
SERVICE_2 = ""
SERVICE_3 = ""


@app.get("/")
async def get_config(request: Request):
    """Tests the service and returns the current settings."""
    print(request)
    return {
        "s1_ratio": S1_RATIO,
        "service_1": SERVICE_1,
        "service_2": SERVICE_2,
        "service_3": SERVICE_3
        }

@app.get("/api/v1/")
async def aggregate(request: Request):
    """Is called to aggregate."""
    global SERVICE_1, SERVICE_2, SERVICE_3
    print(request)
    await aggregator.aggregate_requests([SERVICE_1, SERVICE_2, SERVICE_3])
    return {"message": "received"}

@app.post('/ratio/')
async def set_s1_ratio(ratio: models.Ratio):
    """Sets the S1 vs S3 ratio."""
    global S1_RATIO
    S1_RATIO = ratio.ratio
    print(f'Updated S1 ratio to {S1_RATIO}')
    return ratio

@app.post('/targets/')
async def set_target_endpoints(targets: models.Targets):
    """Sets target service endpoints."""
    global SERVICE_1, SERVICE_2, SERVICE_3
    SERVICE_1 = targets.service_1
    SERVICE_2 = targets.service_2
    SERVICE_3 = targets.service_3
    print(f'Setting targets: {SERVICE_1=}, {SERVICE_2=}, {SERVICE_3=}')
    return targets
