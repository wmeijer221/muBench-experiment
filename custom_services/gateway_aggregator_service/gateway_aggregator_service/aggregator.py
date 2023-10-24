"""
Implements simple message aggregator.
"""

import logging
from typing import List, Any, Dict

import asyncio
import aiohttp
from fastapi import Request, HTTPException

from k8s_helper import get_ips_on_k8s_node


BASE_ENDPOINT_HEADER_KEY = "X-BaseEndpoint"
AGGREGATED_ENDPOINT_HEADER_KEY = "X-AggregatedEndpoints"

ENDPOINT_CACHE: Dict[str, List[str]] = dict()

logger = logging.getLogger(__name__)


def build_url(base_endpoint: str, target_endpoint: str) -> str:
    """
    Factory method for URLs for the provided target endpoints.
    If the pod corresponding to one of the endpoins is hosted on the
    same k8s node, its IP addresses are returned, otherwise, the composition
    of the base_endpoint and target endpoint are returned. This function
    assumes the service name is exactly the same as the target endpoint name.
    """
    if not target_endpoint in ENDPOINT_CACHE:
        ips = get_ips_on_k8s_node(app_filter=target_endpoint)
        cached_endpoints = (
            [f"{base_endpoint}{target_endpoint}"]
            if len(ips) == 0
            # TODO: don't hardcode this "/api/v1/" stuff.
            else list([f"{ip}/api/v1" for ip in ips])
        )

        ENDPOINT_CACHE[target_endpoint] = cached_endpoints
        msg = f"Updated endpoint cache: {target_endpoint}={cached_endpoints}."
        logger.info(msg)

    return ENDPOINT_CACHE[target_endpoint]


async def aggregate_requests(request: Request) -> List[bytes]:
    """Performs the requests in parallel and aggregates their results."""
    try:
        base_endpoint = get_base_endpoint(request)
        target_endpoints = get_aggregated_endpoints(request)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=f"Invalid headers: {ex.__cause__}.")
    target_urls = [
        # TODO: Should implement e.g. RR instead of grabbing the first element.
        build_url(base_endpoint, target_endpoint)[0]
        for target_endpoint in target_endpoints
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
