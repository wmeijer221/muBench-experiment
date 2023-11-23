"""Implements some utility functions to help with statistics etc."""

from dataclasses import dataclass
import datetime

import numpy as np
import pandas as pd


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
    """Calculates the average and ignores NaN values."""
    data = [ele for ele in series.values if not np.isnan(ele)]
    return np.average(data)

