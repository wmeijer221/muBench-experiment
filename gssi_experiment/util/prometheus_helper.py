"""Scripts that helps collecting Prometheus CPU utilization data."""

import csv
import datetime
import json
import os
from subprocess import Popen

import dotenv

from gssi_experiment.util.util import (
    get_nested_many,
    better_get_nested_many,
    merge_iterate_through_lists,
)


dotenv.load_dotenv()

DEFAULT_STEP_SIZE_IN_SECONDS = 30
DEFAULT_TARGET_ENDPOINT = "90.147.115.229:30000"

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"


def fetch_service_cpu_utilization(
    output_path: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    target_endpoint: str = DEFAULT_TARGET_ENDPOINT,
    step_size_in_seconds: int = DEFAULT_STEP_SIZE_IN_SECONDS,
):
    """Retrieves CPU utilization information from Prometheus and prints it to a CSV file."""
    tmp_output_path = f"{output_path}.tmp"
    _fetch_service_cpu_utilization_from_prometheus(
        tmp_output_path, start_time, end_time, target_endpoint, step_size_in_seconds
    )
    _parse_prometheus_cpu_utilization_csv(tmp_output_path, output_path)
    # os.remove(tmp_output_path)


def _fetch_service_cpu_utilization_from_prometheus(
    output_path: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    target_endpoint: str = DEFAULT_TARGET_ENDPOINT,
    step_size_in_seconds: int = DEFAULT_STEP_SIZE_IN_SECONDS,
):
    start = start_time.strftime(TIME_FORMAT)
    end = end_time.strftime(TIME_FORMAT)
    prom_user = os.getenv("PROM_USER")
    prom_pass = os.getenv("PROM_PASS")
    # TODO: Implement this with `requests` instead.
    args = [
        "curl",
        "-u",
        f"{prom_user}:{prom_pass}",
        f"http://{target_endpoint}/api/v1/query_range?start={start}&end={end}&step={step_size_in_seconds}s&",
        "--data-urlencode",
        'query=container_cpu_usage_seconds_total{container=~"s.*[0-9].*|gateway.*",service="prometheus-kube-prometheus-kubelet"}',
    ]
    with open(output_path, "w+", encoding="utf-8") as output_file:
        proc = Popen(args, stdout=output_file)
        proc.wait()


def _parse_prometheus_cpu_utilization_csv(input_path: str, output_path: str):
    # Read input JSON data.
    with open(input_path, "r", encoding="utf-8") as input_file:
        json_data = json.loads(input_file.read())
        containers = better_get_nested_many(
            json_data, key=["data", "result", "metric", "container"]
        )
        values = get_nested_many(json_data, key=["data", "result", "values"])
    # Write parsed CSV data.
    with open(output_path, "w+", encoding="utf-8") as output_file:
        csv_writer = csv.writer(output_file)
        csv_writer.writerow(containers)
        # The first element is the timestamp.
        sorting_key = lambda datapoint: datapoint[0]
        for timestamp, element in merge_iterate_through_lists(values, sorting_key):
            formatted_timestamp = datetime.datetime.fromtimestamp(timestamp)
            data_row = [
                (element[key][1] if key in element else "")
                for key, _ in enumerate(containers)
            ]
            data_row = [formatted_timestamp, *data_row]
            csv_writer.writerow(data_row)


# Test code
# fetch_service_cpu_utilization(
#     "./testfile.csv",
#     datetime.datetime(2023, 11, 8, 19),
#     datetime.datetime(2023, 11, 10, 5),
# )
