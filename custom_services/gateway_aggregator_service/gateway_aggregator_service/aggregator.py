"""
Implements message aggregator.
"""

from typing import Iterator
import asyncio
import aiohttp


async def get(url, session: aiohttp.ClientSession):
    """Makes get request asynchronously."""
    try:
        print(f'Making request to "{url}"')
        async with session.get(url=url) as response:
            resp = await response.read()
            if response.status % 100 == 2:
                print(f"Successfully got url {url} with resp of length {len(resp)}.")
            else:
                print(f'Failed request to url {url} with statuscode {response.status}.')
            return resp
    except Exception as e:
        print(f"Unable to get url {url} due to {e.__class__}.")
        raise e

async def aggregate_requests(target_urls: Iterator[str]):
    """Performs the requests in parallel and aggregates their results."""
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[get(url, session) for url in target_urls])
        print(ret)
