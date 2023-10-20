from typing import List
import random
import urllib.parse

import sys

QUERY_PARAMETER_KEY = "QueryParameters"


def build_query_builder_from_runner_parameters(runner_parameters: dict):
    """Factory method that uses Runner parameters."""
    if QUERY_PARAMETER_KEY not in runner_parameters:
        return NoQueryString()
    query_params = runner_parameters[QUERY_PARAMETER_KEY]
    return build_query_builder(query_params["type"], query_params["parameters"])


def build_query_builder(query_type: str, parameters: dict):
    """Factory methat that uses explicit type."""
    print(f"Building query builder: {query_type}.")
    query_builder = getattr(sys.modules[__name__], query_type)
    return query_builder(**parameters)


class QueryStringBuilder:
    """Base class for query string builders."""

    def build_query(self) -> str:
        raise NotImplementedError()


class NoQueryString(QueryStringBuilder):
    """When no queries are generated."""

    def build_query(self) -> str:
        return ""


class AggregatedRequestBuilder(QueryStringBuilder):
    def __init__(self, endpoints: List[str], probabilities: List[float]) -> None:
        self.__endpoints = endpoints
        self.__probabilities = probabilities

    def build_query(self) -> str:
        targets = [
            endpoint
            for (endpoint, probability) in zip(self.__endpoints, self.__probabilities)
            if random.random() <= probability
        ]

        return {
            "mything": "asdf"
        }
