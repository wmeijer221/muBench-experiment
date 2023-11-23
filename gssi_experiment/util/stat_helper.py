import numpy as np
import pandas as pd

from dataclasses import dataclass
import datetime


def mape(expected: pd.Series, real: pd.Series) -> float:
    """Calculates the mean average percentage error."""
    m = 0
    for real_ele, expected_ele in zip(expected, real):
        m += abs((expected_ele - real_ele) / expected_ele)
    m /= len(expected)
    m *= 100
    return m


def mae(expected: pd.Series, real: pd.Series) -> float:
    """Calculates the mean absolute error."""
    m = 0
    for real_ele, expected_ele in zip(expected, real):
        m += abs((real_ele - expected_ele))
    m /= len(expected)
    return m


def non_nan_avg(series: pd.Series) -> float:
    data = [ele for ele in series.values if not np.isnan(ele)]
    return np.average(data)


def calculate_average_cpu_time(experiment_folder: str, services: list):
    """Calculates average CPU time using Prometheus' raw data."""

    data_path = f"{experiment_folder}/cpu_utilization_raw.csv"
    cpu_data = pd.read_csv(data_path)


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
            return f"{self.prev_timestamp=}, {self.prev_value=}, {self.total=}, {self.count=}"

    def __calculate_avg_cpu_time(services):
        cols = ["timestamp", *services]

        tested_data = cpu_data[cols].copy()
        tested_data.dropna(how="all", inplace=True, subset=services)
        tested_data = tested_data.reset_index().drop("index", axis=1)

        entries = {service: Entry() for service in services}

        for row in tested_data.iterrows():
            row_data = row[1]
            for service in services:
                entry = row_data[service]
                # NaN values are ignored.
                # Rows generally have only one non-NaN value.
                if np.isnan(entry):
                    continue
                # Sets initial value for x and y.
                if entries[service].prev_value is None:
                    entries[service].prev_value = row_data[service]
                    entries[service].prev_timestamp = row_data["timestamp"]
                    continue
                # Calculates changes in time (x).
                prev_timestamp = datetime.datetime.strptime(
                    entries[service].prev_timestamp, "%Y-%m-%d %H:%M:%S.%f"
                )
                curr_timestamp = datetime.datetime.strptime(
                    row_data["timestamp"], "%Y-%m-%d %H:%M:%S.%f"
                )
                dx = (curr_timestamp - prev_timestamp).total_seconds()
                # calculates change in CPU usage (y).
                dy = entry - entries[service].prev_value
                # calculates derivative and updates values
                entries[service].total += dy / dx
                entries[service].count += 1
                entries[service].prev_value = entry
                entries[service].prev_timestamp = row_data["timestamp"]

        # Calculates the average.
        try:
            avg = [entry.total / entry.count for _, entry in entries.items()]
            return list(avg)
        except ZeroDivisionError:
            new_services = []
            for service, entry in entries.items():
                if entry.count == 0:
                    chunks = service.split(".")
                    if len(chunks) == 1:
                        faulty_service = f'{chunks[0]}.1'
                    else:
                        faulty_service = f"{chunks[0]}.{int(chunks[1]) + 1}"
                    new_services.append(faulty_service)
                else:
                    new_services.append(service)
            print(f"Retrying to calculate averages with services: {new_services}")
            return __calculate_avg_cpu_time(new_services)

    return __calculate_avg_cpu_time(services)
