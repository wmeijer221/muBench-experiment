"""
Implements simple gateway aggregator.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import aggregator


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://0.0.0.0:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/")
async def aggregate(request: Request):
    """Is called to aggregate."""
    result = await aggregator.aggregate_requests(request)
    return result
