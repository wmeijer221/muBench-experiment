"""
Implements a bunch of code that help with dealing with raw prometheus data.
When using this only `calculate_average_cpu_time` is relevant. The other stuff
are all inner functions that deal with NaN value magic, and ensure the calculation 
actually works and yields the right result.

The main idea is that it attempts to calculate the average CPU usage of the provided
services during the provided timespan. If it fails to do so, it alters the service names,
assuming they contain a mistake and retries to calcualte the average cpu usage for those.
"""

import datetime
from dataclasses import dataclass
from typing import Iterator, Dict, List
import itertools

import pandas as pd
import numpy as np

TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
TIMESTAMP_KEY = "timestamp"
PARSED_TIMESTAMP_KEY = "parsed_timestamp"

MAX_RETRIES = 10
__retries = 0


@dataclass()
class Entry:
    """
    Data class for calculating average CPU usage over time.
    """

    prev_value = None
    prev_timestamp = None
    total = 0
    count = 0

    # HACK: Same reason as in `__build_initial_services`.
    def __init__(self, total: int = 0, count: int = 0) -> None:
        self.total = total
        self.count = count

    def __str__(self) -> str:
        return (
            f"{self.prev_timestamp=}, {self.prev_value=}, {self.total=}, {self.count=}"
        )


# TODO: Change all of this to be a class.


def calculate_average_cpu_time(
    experiment_folder: str,
    service_cols: list,
    start_time: datetime.datetime,
    end_time: datetime.date,
):
    """Calculates average CPU time using Prometheus' raw data."""
    global __retries

    __retries = 0
    data_path = f"{experiment_folder}/cpu_utilization_raw.csv"
    df = pd.read_csv(data_path)
    service_cols = __build_initial_services(df, service_cols)
    df = add_parsed_timestamp(df)
    df = df[df[PARSED_TIMESTAMP_KEY] >= start_time]
    df = df[df[PARSED_TIMESTAMP_KEY] <= end_time]
    return __calculate_avg_cpu_time(df, service_cols)


def __build_initial_services(
    df: pd.DataFrame, service_cols: Iterator[str]
) -> Iterator[str]:
    # HACK: Only necessary when the column suffix indices aren't set correctly (e.g., 'gw.1' exists but 'gw' doesn't).
    new_service_cols = service_cols
    for _ in range(MAX_RETRIES):
        service_has_col_in_df = [serv in df.columns for serv in new_service_cols]
        if all(service_has_col_in_df):
            return new_service_cols
        else:
            fake_entries = {
                serv: Entry(count=1) if is_present else Entry(count=0)
                for serv, is_present in zip(new_service_cols, service_has_col_in_df)
            }
            new_service_cols = __build_new_services(fake_entries)
            print(f"Updating initial services to: {new_service_cols}")

    raise ValueError(f"Could not find requested services in df: {service_cols}.")


def add_parsed_timestamp(df: pd.DataFrame):
    """Adds a parsed `datetime` timestamp to `df`."""

    def __reshape_timestamp(series: pd.Series):
        """Applies `datetime.strptme` to a `pd.Series`."""
        data = []
        for ele in series.values:
            try:
                parsed = datetime.datetime.strptime(ele, TIME_FORMAT)
            except ValueError:
                parsed = ""
            data.append(parsed)
        ser = pd.Series(data)
        return ser

    df = df.copy()
    df[PARSED_TIMESTAMP_KEY] = df[TIMESTAMP_KEY].transform(__reshape_timestamp)
    # Removes entries with invalid datetime formats;
    # which are marked by empty strings.
    invalid_dates = df[df[PARSED_TIMESTAMP_KEY] == ""]
    df = df.drop(invalid_dates.index)
    return df


def calculate_average_cpu_time_from_df(
    df: pd.DataFrame, service_cols: Iterator[str]
) -> List[float]:
    """Does the ame as ``calculate_average_cpu_time``, however,
    with fewer assurances that the calculation will work."""
    return __calculate_avg_cpu_time(df, service_cols)


def __calculate_avg_cpu_time(
    df: pd.DataFrame, service_cols: Iterator[str]
) -> List[float]:
    """
    Helper function that can be recursively called.
    Attempts to calculate the averages with the given services.
    """
    cols = [TIMESTAMP_KEY, *service_cols]

    tested_data = df[cols].copy()
    tested_data.dropna(how="all", inplace=True, subset=service_cols)
    tested_data = tested_data.reset_index().drop("index", axis=1)

    # Tests if the names are present or not.
    entries = __calculate_entries(tested_data, service_cols)

    # Calculates the average.
    try:
        avg = [entry.total / entry.count for _, entry in entries.items()]
    except ZeroDivisionError:
        avg = __retry_calculation(df, entries)

    return list(avg)


def __calculate_entries(df: pd.DataFrame, service_col: Iterator[str]):
    entries = {service: Entry() for service in service_col}

    for row, service in itertools.product(df.iterrows(), service_col):
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


def __retry_calculation(df: pd.DataFrame, entries: Iterator[Entry]):
    """
    Figures out what service caused the error,
    and composes an updated list of service names
    to retry with.
    """

    global __retries

    if __retries >= MAX_RETRIES:
        raise ValueError(
            "Failed to calculate average CPU utilization with provided services."
        )
    __retries += 1

    new_service_cols = __build_new_services(entries)

    # Retries with the new list.
    print(f"Retrying to calculate averages with services: {new_service_cols}")
    return __calculate_avg_cpu_time(df, new_service_cols)


def __build_new_services(entries: Dict[str, Entry]) -> Iterator[str]:
    def __build_next_service_col(service_col: str) -> str:
        """Adds an index as a suffix."""
        name_chunks = service_col.split(".")
        if len(name_chunks) == 1:
            return f"{name_chunks[0]}.1"
        else:
            return f"{name_chunks[0]}.{int(name_chunks[1]) + 1}"

    new_service_cols = []
    for service_col, entry in entries.items():
        if entry.count == 0:
            # This entry caused the error, so a new
            # entry name is composed.
            new_service_col = __build_next_service_col(service_col)
            new_service_cols.append(new_service_col)
        else:
            # non-guilty services are simply forwarded.
            new_service_cols.append(service_col)

    return new_service_cols
