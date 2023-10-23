"""
Implements simple message aggregator.
"""

from typing import List, Any
import asyncio
import aiohttp
from fastapi import Request, HTTPException


BASE_ENDPOINT_HEADER_KEY = "X-BaseEndpoint"
AGGREGATED_ENDPOINT_HEADER_KEY = "X-AggregatedEndpoints"


async def aggregate_requests(request: Request) -> List[bytes]:
    """Performs the requests in parallel and aggregates their results."""
    try:
        base_endpoint = get_base_endpoint(request)
        target_endpoints = get_aggregated_endpoints(request)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"Invalid headers: {ex.__cause__}.")
    target_urls = [
        f"{base_endpoint}{target_endpoint}" for target_endpoint in target_endpoints
    ]
    result = await get_many(target_urls)
    return result


def get_base_endpoint(request: Request) -> str:
    """Returns the base endpoint for the request."""
    base = request.headers.get(BASE_ENDPOINT_HEADER_KEY)
    if base is None:
        raise KeyError(f'Header "{BASE_ENDPOINT_HEADER_KEY}" is missing.')
    return base


def get_aggregated_endpoints(request: Request) -> List[str]:
    """Extracts aggregated endpoints from the provided request."""
    aggregate_endpoints = request.headers.get(AGGREGATED_ENDPOINT_HEADER_KEY)
    if aggregate_endpoints is None:
        raise KeyError(f'Header "{AGGREGATED_ENDPOINT_HEADER_KEY}" is missing.')
    endpoints = aggregate_endpoints.split(",")
    return endpoints


async def get_many(urls: List[str]) -> List[Any]:
    """Performs multiple GET requests in parallel."""
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[get(url, session) for url in urls])
    return ret


async def get(url, session: aiohttp.ClientSession) -> bytes:
    """Makes GET request and returns the response."""
    try:
        print(f'Making request to "{url}"')
        async with session.get(url=url) as response:
            resp = await response.read()
            if response.status / 100 == 2:
                print(f"Successfully got url {url} with resp of length {len(resp)}.")
            else:
                print(f"Failed request to url {url} with statuscode {response.status}.")
            return resp
    except Exception as e:
        print(f"Unable to get url {url} due to {e.__class__}.")
        raise e
