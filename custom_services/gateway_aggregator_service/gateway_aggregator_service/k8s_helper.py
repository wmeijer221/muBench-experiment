"""
Implements variosu helper functions to interface with the Kubernetes API.
"""

import logging
from typing import List

from kubernetes import client, config
from kubernetes.client import V1Pod

from util import getenv_non_null

logger = logging.getLogger(__name__)


def get_ips_on_k8s_node(
    app_filter: str = None, namespace_filter: str = None, filter_local_node: bool = True
) -> List[str]:
    """
    Returns the IP addresses of the pods running on the same node.
    Uses a NAME_FILTER and a NAMESPACE_FILTER, which are both
    environment variables.
    """

    _load_k8s_config()
    # TODO: Add option to ignore node alltogether.
    node_name = getenv_non_null("MY_NODE_NAME")

    # Performs search.
    v1 = client.CoreV1Api()
    field_selector = f"spec.nodeName={node_name}" if filter_local_node else None
    if not namespace_filter is None:
        field_selector = f"{field_selector},metadata.namespace={namespace_filter}"
    label_selector = f"app={app_filter}" if not app_filter is None else None
    pods: List[V1Pod] = v1.list_pod_for_all_namespaces(
        watch=False, field_selector=field_selector, label_selector=label_selector
    ).items

    # Filters results.
    node_ips = []
    for pod in pods:
        if not hasattr(pod.status, "pod_i_ps") or pod.status.pod_i_ps is None:
            continue
        ips = [entry.ip for entry in pod.status.pod_i_ps]
        node_ips.extend(ips)

    return node_ips


def _load_k8s_config():
    try:
        config.load_incluster_config()
    except config.ConfigException:
        logger.warning("Not running inside k8s, using alternative config source.")
        config.load_kube_config()
