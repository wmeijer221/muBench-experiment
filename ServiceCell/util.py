from typing import Dict, Any, TypeVar


V = TypeVar("V")
K = TypeVar("K")


def safe_get(collection: Dict[K, V], key: K, default: V = None) -> V:
    """
    Returns the value of the specified key if it exists.
    Otherwise, it returns the default value.
    """
    if key not in collection.keys():
        return default
    return collection[key]
