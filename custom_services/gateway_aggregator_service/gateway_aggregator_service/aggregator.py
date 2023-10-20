"""
Implements simple message aggregator.
"""

from typing import List, Any
import asyncio
import aiohttp
from fastapi import Request


async def aggregate_requests(request: Request) -> List[bytes]:
    """Performs the requests in parallel and aggregates their results."""
    base_endpoint = get_base_endpoint(request)
    target_endpoints = get_aggregated_endpoints(request)
    target_urls = [
        f"{base_endpoint}{target_endpoint}" for target_endpoint in target_endpoints
    ]
    result = await get_many(target_urls)
    return result


def get_base_endpoint(request: Request) -> str:
    """Returns the base endpoint for the request."""
    return request.headers.get("X-BaseEndpoint")


def get_aggregated_endpoints(request: Request) -> List[str]:
    """Extracts aggregated endpoints from the provided request."""
    aggregate_endpoints = request.headers.get("X-AggregatedEndpoints")
    return aggregate_endpoints.split(",")


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
