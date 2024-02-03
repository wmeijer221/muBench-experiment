import typing
import math
from numbers import Number


import pandas as pd
import matplotlib.pyplot as plt

from gssi_experiment.util.util import safe_save_fig


def to_averaged_df(
    df: pd.DataFrame,
    group_on: "str | typing.Iterator[str]",
    averaged_columns: typing.Iterator[str],
) -> pd.DataFrame:
    if isinstance(group_on, str):
        group_on = [group_on]
    # averaged_columns = ["avg_latency_ms", *cpu_columns, *synth_cpu_cols]
    print(f"{averaged_columns=}")
    grp_df: pd.DataFrame = df.select_dtypes(include="number")
    grp_df = grp_df.groupby(group_on)

    avg_df: pd.DataFrame = grp_df.mean(averaged_columns)

    # Sets standard deviation
    std_df: pd.DataFrame = grp_df.std()
    std_df.columns = [f"std_{col}" for col in std_df.columns if not col in group_on]
    avg_df = avg_df.merge(std_df, on=group_on)

    if len(group_on) > 1:
        for i, key in enumerate(group_on):
            avg_df[key] = [val[i] for val in avg_df.index]
    else:
        avg_df[group_on[0]] = avg_df.index

    avg_df = avg_df.reset_index(drop=True)

    return avg_df


def create_figure(
    df: pd.DataFrame,
    x_key: str,
    synth_key: str,
    real_key: str,
    y_axis: str,
    output_path: "str | None" = None,
):
    # Create a figure and axis
    plt.figure()
    ax = plt.axes()

    # Plot the first line (sine function)
    ax.plot(df[x_key], df[synth_key], label="Theoretical", color="blue")

    # Plot the second line (cosine function)
    ax.plot(df[x_key], df[real_key], label="Experimental", color="red")
    upper = df[real_key] + df[f"std_{real_key}"]
    lower = df[real_key] - df[f"std_{real_key}"]
    ax.fill_between(df[x_key], upper, lower, facecolor="red", alpha=0.25)

    # Add labels and a legend
    ax.set_ylabel(y_axis)
    ax.set_xlabel(de_snake_case(x_key))
    # ax.set_title("Theoretical and experimental results for response latency")
    ax.legend()

    # Show the plot
    if output_path:
        print(f"{output_path=}")
        safe_save_fig(output_path)
    else:
        plt.show()


def create_split_multiline_figure(
    df: pd.DataFrame,
    split_key: str,
    x_key: str,
    y_key: str,
    y_key2: str,
    output_path: "str | None" = None,
):
    _, axes = plt.subplots(1, 2, figsize=(12, 4))
    exp_ax, synth_ax = axes[0], axes[1]

    splits = df[split_key].unique()

    for split in splits:
        sub_df = df[df[split_key] == split]
        label = f"{de_snake_case(split_key)} = {split}"
        exp_ax.plot(sub_df[x_key], sub_df[y_key], label=label)
        std_key = f"std_{y_key}"
        if std_key in sub_df.columns:
            upper = sub_df[y_key] + sub_df[std_key]
            lower = sub_df[y_key] - sub_df[std_key]
            exp_ax.fill_between(sub_df[x_key], lower, upper, alpha=0.25)

        synth_ax.plot(sub_df[x_key], sub_df[y_key2], label=label)
        std_key = f"std_{y_key2}"
        if std_key in sub_df.columns:
            upper = sub_df[y_key2] + sub_df[std_key]
            lower = sub_df[y_key2] - sub_df[std_key]
            synth_ax.fill_between(sub_df[x_key], lower, upper, alpha=0.25)

    exp_ax.legend()
    synth_ax.legend()

    plt.tight_layout()

    # Show the plot
    if output_path:
        print(f"{output_path=}")
        safe_save_fig(output_path)
    else:
        plt.show()


def create_multi_figure(
    df: pd.DataFrame,
    y_keys: typing.List[str],
    x_key: str,
    split_key: str,
    y_label: str,
    output_path: "str | None" = None,
    num_cols: int = 2,
):
    if split_key:
        splits = df[split_key].unique()
    else:
        splits = [split_key]
    splits.sort()
    num_subplots = len(splits)

    num_rows = math.ceil(num_subplots / num_cols)
    width = 6 * num_cols
    height = 4 * num_rows
    _, axes = plt.subplots(num_rows, num_cols, figsize=(width, height))
    axes = axes.flatten()
    # axes = axes.flatten() if num_rows > 1 else [axes]
    for i, split in enumerate(splits):
        if split_key:
            tmp_df: pd.DataFrame = df[df[split_key] == split]
        else:
            tmp_df: pd.DataFrame = df
        ax: plt.Axes = axes[i]

        tmp_df = tmp_df.sort_values(x_key)
        for y_key in y_keys:
            ax.plot(tmp_df[x_key], tmp_df[y_key], label=de_snake_case(y_key))
            # tmp_df.plot(x_key, y_key, ax=ax)
            std_key = f"std_{y_key}"
            upper = tmp_df[y_key] + tmp_df[std_key]
            lower = tmp_df[y_key] - tmp_df[std_key]
            ax.fill_between(tmp_df[x_key], upper, lower, alpha=0.4)

        ax.set_xlabel(de_snake_case(x_key))
        ax.set_ylabel(y_label)
        ax.set_title(f"{de_snake_case(split_key)} = {split}")
        ax.legend()

    plt.tight_layout()

    # Show the plot
    if output_path:
        print(f"{output_path=}")
        safe_save_fig(output_path)
    else:
        plt.show()


def create_plot_comparisons(
    comparison_tuples: typing.List[typing.Tuple[str]],
    df: pd.DataFrame,
    x_column: str,
    output_path: "str | None" = None,
):
    # Calculate the number of subplots based on the length of comparison_tuples
    num_subplots = len(comparison_tuples)
    # Determine the number of rows and columns for the subplots
    num_rows = math.ceil(num_subplots / 2)  # Assuming 2 columns
    num_cols = 2  # Number of columns for the subplots

    # Create a larger figure with subplots
    width = 6 * num_cols
    height = 4 * num_rows
    _, axes = plt.subplots(num_rows, num_cols, figsize=(width, height))

    # Flatten the axes array if there is more than one row
    axes = axes.flatten() if num_rows > 1 else [axes]

    for i, columns in enumerate(comparison_tuples):
        # Select the current subplot
        ax: plt.Axes = axes[i]

        # Plot a line diagram for each pair of columns in the DataFrame
        for column in columns:
            ax.plot(df[x_column], df[column], label=de_snake_case(column))
            std_key = f"std_{column}"
            upper = df[column] + df[std_key]
            lower = df[column] - df[std_key]
            ax.fill_between(df[x_column], upper, lower, alpha=0.4)

        ax.set_xlabel(de_snake_case(x_column))
        ax.set_ylabel("CPU utilization")
        ax.legend()

    # Adjust layout to prevent overlapping titles
    plt.tight_layout()
    if output_path:
        print(f"{output_path=}")
        safe_save_fig(output_path)
    else:
        plt.show()


def de_snake_case(word: str) -> str:
    chunks = word.split("_")
    chunks = [chunk[0].upper() + chunk[1:] for chunk in chunks]
    word = " ".join(chunks)
    return word


def normalize_field(df: pd.DataFrame, field: str) -> pd.DataFrame:
    def normalize(x, x_min, x_max):
        x -= x_min
        x /= x_max - x_min
        return x

    min_x, max_x = min(df[field]), max(df[field])
    df.loc[:, field] = df[field].transform(lambda x: normalize(x, min_x, max_x))
    return df


def normalize_field_and_yield_min_max(
    df: pd.DataFrame, field: str
) -> typing.Tuple[pd.DataFrame, Number, Number]:
    df = df.copy()
    min_x, max_x = min(df[field]), max(df[field])
    df.loc[:, field] = df[field].transform(lambda x: normalize(x, min_x, max_x))
    return df, min_x, max_x


def normalize(x, x_min, x_max):
    x -= x_min
    x /= x_max - x_min
    return x


def reset_column_name_indices(df: pd.DataFrame):
    """Resets the suffix indices of dataframe columns."""

    def __get_real_name(col: str) -> str:
        return col.split(".")[0]

    columns = df.columns
    unique_cols = set([__get_real_name(col) for col in columns])
    appearances = {col: 0 for col in unique_cols}
    new_cols = []
    for col in columns:
        real_name = __get_real_name(col)
        if appearances[real_name] == 0:
            new_cols.append(real_name)
        else:
            new_name = f"{real_name}.{appearances[real_name]}"
            new_cols.append(new_name)
        appearances[real_name] += 1

    was_updated = any(old != new for old, new in zip(df.columns, new_cols))
    if was_updated:
        print(f"Updated df columns to: {new_cols}")

    df.columns = new_cols
