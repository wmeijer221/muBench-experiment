"""Scripts that helps collecting Prometheus CPU utilization data."""

import csv
import datetime
import json
import os
from subprocess import Popen
from warnings import warn

import requests
from requests.auth import HTTPBasicAuth
import regex as re

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


class CpuUtilizationFetcher:
    """
    Collects CPU Utilization data from prometheus by querying the API.
    This yields aggregated and noisy results.
    """

    def __init__(
        self,
        output_path: str,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
        step_size_in_minutes: int = DEFAULT_WINDOW_SIZE_IN_MINUTES,
        time_offset_in_minutes: int = 0,
    ) -> None:
        warn("Class `CpuUtilizationFetcher` is deprecated.")
        self.__output_path = os.path.abspath(output_path)
        self.__tmp_output_path = f"{self.__output_path}.tmp"
        self.__start_time = start_time
        self.__end_time = end_time
        self.__step_size_in_minutes = step_size_in_minutes
        self.__time_offset_in_minutes = time_offset_in_minutes

    def fetch_service_cpu_utilization(self):
        """Retrieves CPU utilization information from Prometheus and prints it to a CSV file."""
        # Offsets query times by some constant.
        time_offset = datetime.timedelta(minutes=self.__time_offset_in_minutes)
        self.__start_time += time_offset
        self.__end_time += time_offset
        # Fetches and parses data.
        self.__fetch_service_cpu_utilization_from_prometheus()
        self.__parse_prometheus_cpu_utilization_csv()
        os.remove(self.__tmp_output_path)

    def __fetch_service_cpu_utilization_from_prometheus(self):
        step_size_in_seconds = round(self.__step_size_in_minutes * 60)
        prom_user = os.getenv("PROM_USER")
        prom_pass = os.getenv("PROM_PASS")
        target_endpoint = os.getenv("PROMETHEUS_API_ENDPOINT")

        if os.getenv("USE_MINIKUBE", "false") == "true":
            print(
                "REMINDER THAT THE PROMETHEUS QUERY SOMEHOW DOESN'T WORK IN MINIKUBE."
            )

        offset = datetime.timedelta(minutes=self.__time_offset_in_minutes)

        start = self.__start_time + offset
        end = self.__end_time + offset
        start = start.strftime(TIME_FORMAT)
        end = end.strftime(TIME_FORMAT)
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
        print(f'Outputting raw Prometheus data to "{self.__tmp_output_path}".')
        with open(self.__tmp_output_path, "w+", encoding="utf-8") as output_file:
            proc = Popen(args, stdout=output_file)
            proc.wait()

    def __parse_prometheus_cpu_utilization_csv(self):
        # Read input JSON data.
        with open(self.__tmp_output_path, "r", encoding="utf-8") as input_file:
            json_data = json.loads(input_file.read())
            containers = better_get_nested_many(
                json_data,
                key=["data", "result", "metric", "container"],
            )
            values = get_nested_many(json_data, key=["data", "result", "values"])

        # Write parsed CSV data.
        with open(self.__output_path, "w+", encoding="utf-8") as output_file:
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


class LatestCpuUtilizationFetcher:
    def __init__(
        self,
        output_path: str,
        time_window_in_minutes: int,
        start_time: datetime.datetime,
    ) -> None:
        self.__output_path = os.path.abspath(output_path)
        self.__tmp_output_path = f"{self.__output_path}.tmp"
        self.__time_window_in_minutes = time_window_in_minutes
        self.__start_time = start_time

    def fetch_latest_cpu_utilization(
        self, fetch_new_data: bool = True, delete_tmp: bool = True
    ):
        """Does the same thing as V1, just differently."""
        if fetch_new_data:
            self.__fetch_latest_cpu_utilization_from_prometheus()
        self.__parse_prometheus_cpu_utilization_csv_v2()
        self.__prioritize_entries()
        if delete_tmp:
            os.remove(self.__tmp_output_path)

    def __fetch_latest_cpu_utilization_from_prometheus(self):
        prom_user = os.getenv("PROM_USER")
        prom_pass = os.getenv("PROM_PASS")
        target_endpoint = os.getenv("PROMETHEUS_API_ENDPOINT")

        endpoint = f"{target_endpoint}/api/v1/query"
        url_params = {
            "query": f"container_cpu_usage_seconds_total[{self.__time_window_in_minutes}m]"
        }

        auth = HTTPBasicAuth(prom_user, prom_pass)
        response = requests.get(endpoint, params=url_params, auth=auth)
        print(f"Prometheus response status: {response.status_code}")

        with open(self.__tmp_output_path, "w+", encoding="utf-8") as output_file:
            output_file.write(response.text)

    def __parse_prometheus_cpu_utilization_csv_v2(self):
        """Does the same as v1 but differently."""

        def __get_container_name(entry) -> "str | None":
            if os.getenv("USE_MINIKUBE", "false").lower() == "true":
                print("USING THE MINIKUBE SETTINGS")
                # HACK: Somehow `container` doesn't exist in Minikube deployments.
                if not "pod" in entry["metric"]:
                    return None
                # Removes the random string at the end of the name.
                entry = entry["metric"]["pod"].split("-")[0:-1]
                entry = "-".join(entry)
                if not re.match(r"s[0-9].*", entry):
                    return None
                return entry
            else:
                if not "container" in entry["metric"]:
                    return None
                return entry["metric"]["container"]

        with open(self.__tmp_output_path, "r", encoding="utf-8") as input_file:
            j_data = json.loads(input_file.read())

        containers = list()
        datas = list()
        for entry in j_data["data"]["result"]:
            container = __get_container_name(entry)
            if container is None:
                continue
            containers.append(container)
            data = entry["values"]
            datas.append(data)
        print(f"Found {containers=}")

        sorting_key = lambda datapoint: datapoint[0]
        with open(self.__output_path, "w+", encoding="utf-8") as output_file:
            csv_writer = csv.writer(output_file)
            header_row = ["timestamp", *containers]
            csv_writer.writerow(header_row)
            counter = 0
            for timestamp, value in merge_iterate_through_lists(datas, sorting_key):
                formatted_timestamp = datetime.datetime.fromtimestamp(timestamp)
                if formatted_timestamp < self.__start_time:
                    continue
                data_row = [
                    (value[key][1] if key in value else "")
                    for key, _ in enumerate(containers)
                ]
                data_row = [formatted_timestamp, *data_row]
                csv_writer.writerow(data_row)
                counter += 1
            print(f"Wrote {counter} CPU utilization entries.")

    def __prioritize_entries(self):
        """Prioritizes entries based on their appearance so the data is analyzed in the right order."""
        with open(self.__output_path, "r", encoding="utf-8") as input_file:
            csv_reader = csv.reader(input_file)
            header = next(csv_reader)

            counter = [0] * (len(header) - 1)
            first = [-1] * len(counter)
            rows = []
            for row_idx, row in enumerate(csv_reader):
                rows.append(row)
                for col_idx, col in enumerate(row[1:]):
                    if col != "":
                        # Counts entries per service.
                        counter[col_idx] += 1
                        # Updates the first appearance of the element.
                        if first[col_idx] == -1:
                            first[col_idx] = row_idx

        # Collects the found entries per column.
        entries = {ele: [] for ele in set(header[1:])}
        for idx, (key, first) in enumerate(zip(header[1:], first)):
            if first == -1:
                continue
            entries[key].append((idx, first))

        # Generates new header based on the first appearance.
        header = list(header)
        for key, vals in entries.items():
            vals = sorted(vals, key=lambda x: -x[1])

            for c, (idx, _) in enumerate(vals):
                if c == 0:
                    continue
                header[idx] = f"{header[idx]}.{c}"

        def __filter_row(row):
            return [
                row[0],
                *[col for col_idx, col in enumerate(row[1:]) if counter[col_idx] > 0],
            ]

        with open(self.__output_path, "w+", encoding="utf-8") as output_file:
            csv_writer = csv.writer(output_file)
            new_header = __filter_row(header)
            print(f"{new_header=}")
            csv_writer.writerow(new_header)
            for row in rows:
                new_row = __filter_row(row)
                csv_writer.writerow(new_row)
