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

DEFAULT_WINDOW_SIZE_IN_MINUTES = 2
DEFAULT_STEP_SIZE_IN_SECONDS = 120

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.000Z"


def fetch_service_cpu_utilization(
    output_path: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    step_size_in_minutes: int = DEFAULT_WINDOW_SIZE_IN_MINUTES,
):
    """Retrieves CPU utilization information from Prometheus and prints it to a CSV file."""
    tmp_output_path = f"{output_path}.tmp"
    _fetch_service_cpu_utilization_from_prometheus(
        tmp_output_path, start_time, end_time, step_size_in_minutes
    )
    _parse_prometheus_cpu_utilization_csv(tmp_output_path, output_path)
    os.remove(tmp_output_path)


def _fetch_service_cpu_utilization_from_prometheus(
    output_path: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    step_size_in_minutes: int = DEFAULT_WINDOW_SIZE_IN_MINUTES,
):
    step_size_in_seconds = round(step_size_in_minutes * 60)
    start = start_time.strftime(TIME_FORMAT)
    end = end_time.strftime(TIME_FORMAT)
    prom_user = os.getenv("PROM_USER")
    prom_pass = os.getenv("PROM_PASS")
    target_endpoint = os.getenv("PROMETHEUS_API_ENDPOINT")

    if os.getenv("USE_MINIKUBE", "false") == "true":
        print("REMINDER THAT THE PROMETHEUS QUERY SOMEHOW DOESN'T WORK IN MINIKUBE.")

    # TODO: Implement this with `requests` instead.
    args = [
        "curl",
        "-u",
        f"{prom_user}:{prom_pass}",
        f"{target_endpoint}/api/v1/query_range?start={start}&end={end}&step={DEFAULT_STEP_SIZE_IN_SECONDS}s&",
        "--data-urlencode",
        'query=sum by (container) (increase(container_cpu_usage_seconds_total{container=~"s.*[0-9].*|gateway.*|gw",service="prometheus-kube-prometheus-kubelet"}'
        + f"[{step_size_in_seconds}s])/{step_size_in_seconds})",
    ]
    print(args)
    print(f'Outputting raw Prometheus data to "{output_path}".')
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
        csv_writer.writerow(["timestamp", *containers])
        # The first element is the timestamp.
        counter = 0
        sorting_key = lambda datapoint: datapoint[0]
        for timestamp, element in merge_iterate_through_lists(values, sorting_key):
            formatted_timestamp = datetime.datetime.fromtimestamp(timestamp)
            data_row = [
                (element[key][1] if key in element else "")
                for key, _ in enumerate(containers)
            ]
            data_row = [formatted_timestamp, *data_row]
            csv_writer.writerow(data_row)
            counter += 1
        print(f"Wrote {counter} CPU utilization entries.")


# Test code
# fetch_service_cpu_utilization(
#     "./testfile.csv",
#     datetime.datetime(2023, 11, 8, 19),
#     datetime.datetime(2023, 11, 10, 5),
# )

if __name__ == "__main__":
    fetch_service_cpu_utilization(
        "./test.txt",
        datetime.datetime.strptime("2023-11-20T22:52:35.000Z", TIME_FORMAT),
        datetime.datetime.strptime("2023-11-20T22:59:14.000Z", TIME_FORMAT),
    )
