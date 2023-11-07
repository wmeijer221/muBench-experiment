"""
Implements some helper functions for dealing with json data.
"""

from typing import Any, Collection, Iterator, Tuple, Type
import json
import yaml
from io import TextIOWrapper


class DocumentEditor:
    def load_file(self, source_file: TextIOWrapper) -> Collection:
        raise NotImplementedError()

    def write_file(self, document: Collection, output_file: TextIOWrapper):
        raise NotImplementedError()


class JsonEditor(DocumentEditor):
    def load_file(self, source_file: str) -> Collection:
        return json.loads(source_file.read())

    def write_file(self, document: Collection, output_file: TextIOWrapper):
        output_file.write(json.dumps(document, indent=4))


class YamlEditor(DocumentEditor):
    def load_file(self, source_file: TextIOWrapper) -> Collection:
        yaml_docs = list(yaml.load_all(source_file, yaml.Loader))
        return yaml_docs

    def write_file(self, document: Collection, output_file: TextIOWrapper):
        yaml.dump(document, output_file)


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
    nested_collection: Collection[Any],
    nested_key: Iterator[Any],
    value: Any,
    create_missing_keys: bool = False,
) -> None:
    """
    Returns element in nested collection (e.g., a dict with dicts)
    after searching for it with the nested key.
    """
    current = nested_collection
    for key in nested_key[:-1]:
        if create_missing_keys and isinstance(current, dict) and key not in current:
            current[key] = {}
        current = current[key]
    current[nested_key[-1]] = value


def write_concrete_data_document(
    source_path: str,
    target_path: str,
    overwritten_fields: Iterator[Tuple[Iterator[Any], Any]],
    editor_type: Type[DocumentEditor],
):
    """
    Loads data from the source file, overwrites its
    specified fields, and outputs it to the output file.
    """
    print(f"{source_path=}")
    doc_editor: DocumentEditor = editor_type()
    # Loads data from input path.
    with open(source_path, "r", encoding="utf-8") as source_file:
        doc = doc_editor.load_file(source_file)

    # Overwrites values.
    for nested_key, value in overwritten_fields:
        set_element_in_nested_collection(
            doc, nested_key, value, create_missing_keys=True
        )
    # Writes data to output path.
    with open(target_path, "w+", encoding="utf-8") as output_file:
        doc_editor.write_file(doc, output_file)


# Some tests.
# write_concrete_data_document(
#     "./gssi_experiment/gateway_aggregator/gateway_aggregator_service/service.yaml",
#     "gssi_experiment/gateway_aggregator/gateway_aggregator_service/tmp_service.yaml",
#     [
#         (
#             [3, "spec", "template", "spec", "nodeSelector"],
#             {"kubernetes.io/hostname": "node-3"},
#         )
#     ],
#     editor_type=YamlEditor,
# )

# write_concrete_data_document(
#     "./gssi_experiment/gateway_aggregator/RunnerParameters.json",
#     "./gssi_experiment/gateway_aggregator/tmp_RunnerParameters.json",
#     [
#         (
#             ["RunnerParameters", "HeaderParameters", 0, "parameters", "probabilities"],
#             [0, 0],
#         )
#     ],
#     editor_type=JsonEditor,
# )
