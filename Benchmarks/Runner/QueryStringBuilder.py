"""
Implements a number of header factories.
"""

import random
import sys
from typing import List

HEADER_PARAMETER_KEY = "HeaderParameters"


def build_header_factory_from_runner_parameters(runner_parameters: dict):
    """Factory method that uses Runner parameters."""
    if HEADER_PARAMETER_KEY not in runner_parameters:
        return StaticHeaderFactory()
    query_params = runner_parameters[HEADER_PARAMETER_KEY]
    return build_query_builder(query_params["type"], query_params["parameters"])


def build_query_builder(query_type: str, parameters: dict):
    """Factory methat that uses explicit type."""
    print(f"Building query builder: {query_type}.")
    query_builder = getattr(sys.modules[__name__], query_type)
    return query_builder(**parameters)


class HeaderFactory:
    """Base class for query string builders."""

    def build_headers(self) -> dict:
        """Factory method for headers."""
        raise NotImplementedError()


class StaticHeaderFactory(HeaderFactory):
    """Adds static headers."""

    def __init__(self, **kwargs) -> None:
        self.__kwargs = kwargs

    def build_headers(self) -> dict:
        return self.__kwargs


class AggregatedHeaderFactory(HeaderFactory):
    """Builds header for aggregated request."""

    def __init__(
        self, base_endpoint: str, endpoints: List[str], probabilities: List[float]
    ) -> None:
        self.__base_endpoint = base_endpoint
        self.__endpoints = endpoints
        self.__probabilities = probabilities

    def build_headers(self) -> dict:
        targets = [
            endpoint
            for (endpoint, probability) in zip(self.__endpoints, self.__probabilities)
            if random.random() <= probability
        ]
        targets = ",".join(targets)
        header = {
            "X-BaseEndpoint": self.__base_endpoint,
            "X-AggregatedEndpoints": targets,
        }
        return header
