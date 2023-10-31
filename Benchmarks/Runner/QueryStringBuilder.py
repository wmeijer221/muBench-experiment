"""
Implements a number of header factories.
"""

import random
import sys
from typing import List
import jsonmerge

HEADER_PARAMETER_KEY = "HeaderParameters"


def build_header_factory_from_runner_parameters(
    runner_parameters: dict,
) -> "HeaderFactory":
    """Factory method that uses Runner parameters."""
    if HEADER_PARAMETER_KEY not in runner_parameters:
        return EmptyHeaderFactory()
    # Builds factory chain by iteratively decorating the root.
    root = EmptyHeaderFactory()
    query_params = runner_parameters[HEADER_PARAMETER_KEY]
    for entry in query_params:
        root = build_header_factory(entry["type"], entry["parameters"], root)
    print(f"Built header factory chain: {root.get_chain()}")
    return root


def build_header_factory(
    query_type: str, parameters: dict, inner_factory: "HeaderFactory"
) -> "HeaderFactory":
    """Factory methat that uses explicit type."""
    query_builder = getattr(sys.modules[__name__], query_type)
    return query_builder(inner_factory=inner_factory, **parameters)


class HeaderFactory:
    """Base class for query string builders. Implements simple decorator pattern."""

    def __init__(self, inner_factory: "HeaderFactory | None") -> None:
        if inner_factory is None:
            self._inner_factory = EmptyHeaderFactory()
        else:
            self._inner_factory = inner_factory

    def build_headers(self) -> dict:
        """Factory method for headers."""
        raise NotImplementedError()

    def get_chain(self) -> str:
        return f"{self.__class__.__name__}.{self._inner_factory.get_chain()}"


class EmptyHeaderFactory(HeaderFactory):
    """Returns empty header."""

    def __init__(self, *args, **kwargs) -> None:
        """Empty init."""

    def build_headers(self) -> dict:
        return {}

    def get_chain(self) -> str:
        return self.__class__.__name__


class StaticHeaderFactory(HeaderFactory):
    """Adds static headers."""

    def __init__(self, inner_factory: HeaderFactory, **kwargs) -> None:
        super().__init__(inner_factory)
        self.__kwargs = kwargs

    def build_headers(self) -> dict:
        inner = self._inner_factory.build_headers()
        return jsonmerge.merge(self.__kwargs, inner)


class AggregatedHeaderFactory(HeaderFactory):
    """Builds header for aggregated request."""

    def __init__(
        self,
        inner_factory: HeaderFactory,
        base_endpoint: str,
        endpoints: List[str],
        probabilities: List[float],
    ) -> None:
        super().__init__(inner_factory)
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
            "x-baseendpoint": self.__base_endpoint,
            "x-aggregatedendpoints": targets,
        }

        inner = self._inner_factory.build_headers()
        return jsonmerge.merge(header, inner)


class RequestTypeHeaderFactory(HeaderFactory):
    """Builds header that specifies a message type."""

    def __init__(
        self,
        inner_factory: HeaderFactory,
        request_types: List[str],
        probabilities: List[float],
    ) -> None:
        super().__init__(inner_factory)
        assert len(request_types) == len(probabilities)
        self.__request_types = request_types
        self.__probabilities = probabilities

    def build_headers(self) -> dict:
        total_prob = sum(self.__probabilities)
        rnd = random.random() * total_prob
        prob_sum = 0
        for req_type, prob in zip(self.__request_types, self.__probabilities):
            if (rnd - prob_sum) < prob:
                header = {"x-requesttype": req_type}
                inner = self._inner_factory.build_headers()
                return jsonmerge.merge(header, inner)
            prob_sum += prob
        raise ValueError("This should not be reached.")
