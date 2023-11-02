"""
Implements simple gateway aggregator.
"""

import logging
import os

from fastapi import FastAPI, Request

import aggregator


LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VERSION = "0.0.1"
print(f"{VERSION=}")

app = FastAPI()


@app.get("/api/v1", status_code=200)
@app.get("/api/v1/", status_code=200)
async def aggregate(request: Request):
    """Is called to aggregate."""
    # TODO: the second return value should be respected such that a HTTP 206 response is returned. However, muBench doesn't work with non-200 HTTP codes and immediately yields an 500 status code in non-200 cases.
    result, _ = await aggregator.aggregate_requests(request)
    return result
