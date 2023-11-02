"""
Implements some helper functions for dealing with json data.
"""

from typing import Any, Collection, Iterator, Tuple
import json


def get_element_from_nested_collection(
    nested_collection: Collection[Any], nested_key: Iterator[Any]
) -> Any:
    """
    Returns element in nested collection (e.g., a dict with dicts)
    after searching for it with the nested key.
    """
    current = nested_collection
    for key in nested_key:
        current = current[key]
    return current


def set_element_in_nested_collection(
    nested_collection: Collection[Any], nested_key: Iterator[Any], value: Any
) -> None:
    """
    Returns element in nested collection (e.g., a dict with dicts)
    after searching for it with the nested key.
    """
    current = nested_collection
    for key in nested_key[:-1]:
        current = current[key]
    current[nested_key[-1]] = value


def write_concrete_json_document(
    source_path: str,
    target_path: str,
    overwritten_fields: Iterator[Tuple[Iterator[Any], Any]],
):
    """
    Loads data from the source file, overwrites its
    specified fields, and outputs it to the output file.
    """
    print(f"{source_path=}")
    # Loads data from input path.
    with open(source_path, "r", encoding="utf-8") as source_file:
        json_doc = json.loads(source_file.read())
    # Overwrites values.
    for nested_key, value in overwritten_fields:
        set_element_in_nested_collection(json_doc, nested_key, value)
    # Writes data to output path.
    with open(target_path, "w+", encoding="utf-8") as output_file:
        output_file.write(json.dumps(json_doc, indent=4))
