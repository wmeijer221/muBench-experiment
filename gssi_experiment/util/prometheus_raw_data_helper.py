"""
Implements a bunch of code that help with dealing with raw prometheus data.
When using this only `calculate_average_cpu_time` is relevant. The other stuff
are all inner functions that deal with NaN value magic, and ensure the calculation 
actually works and yields the right result.
"""

import datetime
from dataclasses import dataclass
from typing import Iterator
import itertools

import pandas as pd
import numpy as np

TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
TIMESTAMP_KEY = "timestamp"


@dataclass
class Entry:
    """
    Data class for calculating average CPU usage over time.
    """

    prev_value = None
    prev_timestamp = None
    total = 0
    count = 0

    def __str__(self) -> str:
        return (
            f"{self.prev_timestamp=}, {self.prev_value=}, {self.total=}, {self.count=}"
        )


def calculate_average_cpu_time(
    experiment_folder: str,
    services: list,
    start_time: datetime.datetime,
    end_time: datetime.date,
):
    """Calculates average CPU time using Prometheus' raw data."""

    data_path = f"{experiment_folder}/cpu_utilization_raw.csv"
    cpu_data = pd.read_csv(data_path)
    __add_parsed_timestamp(cpu_data)
    cpu_data = cpu_data[cpu_data["parsed_timestamp"] >= start_time]
    cpu_data = cpu_data[cpu_data["parsed_timestamp"] <= end_time]
    return __calculate_avg_cpu_time(cpu_data, services)


def __add_parsed_timestamp(df: pd.DataFrame):
    df["parsed_timestamp"] = df["timestamp"].transform(__reshape_timestamp)
    # Removes entries with invalid datetime formats;
    # which are marked by empty strings.
    invalid_dates = df[df["parsed_timestamp"] == ""]
    df = df.drop(invalid_dates.index)


def __reshape_timestamp(series: pd.Series):
    data = []
    for ele in series.values:
        try:
            parsed = datetime.datetime.strptime(ele, TIME_FORMAT)
        except:
            parsed = ""
        data.append(parsed)
    ser = pd.Series(data)
    return ser


def __calculate_avg_cpu_time(cpu_data: pd.DataFrame, services: Iterator[str]):
    """
    Helper function that can be recursively called.
    Attempts to calculate the averages with the given services.
    """
    cols = [TIMESTAMP_KEY, *services]

    tested_data = cpu_data[cols].copy()
    tested_data.dropna(how="all", inplace=True, subset=services)
    tested_data = tested_data.reset_index().drop("index", axis=1)

    entries = __calculate_entries(tested_data, services)

    # Calculates the average.
    try:
        avg = [entry.total / entry.count for _, entry in entries.items()]
    except ZeroDivisionError:
        avg = __retry_calculation(cpu_data, entries)

    return list(avg)


def __calculate_entries(tested_data: pd.DataFrame, services: Iterator[str]):
    entries = {service: Entry() for service in services}

    for row, service in itertools.product(tested_data.iterrows(), services):
        row_data = row[1]
        entry = row_data[service]
        # NaN values are ignored.
        # Rows generally have only one non-NaN value.
        if np.isnan(entry):
            continue
        # Sets initial value for x and y.
        if entries[service].prev_value is None:
            entries[service].prev_value = row_data[service]
            entries[service].prev_timestamp = row_data[TIMESTAMP_KEY]
            continue
        # Calculates changes in time (x).
        prev_timestamp = datetime.datetime.strptime(
            entries[service].prev_timestamp, TIME_FORMAT
        )
        curr_timestamp = datetime.datetime.strptime(
            row_data[TIMESTAMP_KEY], TIME_FORMAT
        )
        dx = (curr_timestamp - prev_timestamp).total_seconds()
        # calculates change in CPU usage (y).
        dy = entry - entries[service].prev_value
        # calculates derivative and updates values
        entries[service].total += dy / dx
        entries[service].count += 1
        entries[service].prev_value = entry
        entries[service].prev_timestamp = row_data[TIMESTAMP_KEY]

    return entries


def __retry_calculation(cpu_data: pd.DataFrame, entries: Iterator[Entry]):
    """
    Figures out what service caused the error,
    and composes an updated list of service names
    to retry with.
    """
    new_services = []
    for service, entry in entries.items():
        if entry.count == 0:
            # This entry caused the error, so a new
            # entry name is composed.
            chunks = service.split(".")
            faulty_service = (
                f"{chunks[0]}.1"
                if len(chunks) == 1
                else f"{chunks[0]}.{int(chunks[1]) + 1}"
            )
            new_services.append(faulty_service)
        else:
            # non-guilty services are simply forwarded.
            new_services.append(service)
    # Retries with the new list.
    print(f"Retrying to calculate averages with services: {new_services}")
    return __calculate_avg_cpu_time(cpu_data, new_services)
