import typing

import matplotlib.pyplot as plt
import pandas as pd

from gssi_experiment.util.util import safe_save_fig


DEFAULT_PLOT_STYLE: str = "ggplot"
DEFAULT_OUTPUT_FORMAT: "typing.Iterator[str] | str" = ["png", "pdf"]


def __save_plot(
    figure_output_path: str,
    display_output: bool,
    output_format: "typing.Iterator[str] | str",
):
    if not figure_output_path is None:
        print(f"{figure_output_path=}")

        if isinstance(output_format, str):
            output_format = [output_format]

        for form in output_format:
            safe_save_fig(figure_output_path, display_output, form)
    elif display_output:
        plt.show()


def make_line_chart(
    df: pd.DataFrame,
    x_key: str,
    y_keys: typing.List[str],
    x_label: str,
    y_label: str,
    line_labels: typing.List[str],
    y_std_keys: "typing.List[str | None] | None" = None,
    figure_output_path: "str | None" = None,
    legend_position: "typing.Tuple[str, typing.Tuple[float, float]] | None" = None,
    output_type: "str | typing.Iterator[str]" = DEFAULT_OUTPUT_FORMAT,
    display_output: bool = False,
    style: str = DEFAULT_PLOT_STYLE,
):
    """Creates a line plot with `ggplot` formatting."""

    with plt.style.context(style):
        # Create a figure and axis
        plt.figure()
        ax = plt.axes()

        # Plots lines.
        for index, y_key in enumerate(y_keys):
            # Selects label.
            label = line_labels[index]

            # Plots line
            ax.plot(df[x_key], df[y_key], label=label)

            # Plots std.
            if not y_std_keys is None:
                y_std_key = y_std_keys[index]
                if y_std_key in df.columns:
                    std = df[y_std_key]
                else:
                    std = 0
                upper = df[y_key].add(std)
                lower = df[y_key].subtract(std)
                ax.fill_between(df[x_key], upper, lower, alpha=0.25)

        ax.set_ylabel(y_label)
        ax.set_xlabel(x_label)

        # Sets legend
        if legend_position is None:
            ax.legend()
        else:
            ax.legend(loc=legend_position[0], bbox_to_anchor=legend_position[1])

        __save_plot(figure_output_path, display_output, output_type)


def make_split_line_chart(
    df: pd.DataFrame,
    x_key: str,
    split_key: str,
    y_key: str,
    x_label: str,
    y_label: str,
    build_split_label: callable,
    y_std_key: "str | None" = None,
    figure_output_path: "str | None" = None,
    legend_position: "typing.Tuple[str, typing.Tuple[float, float]] | None" = None,
    display_output: bool = False,
    output_format: "str | typing.Iterator[str]" = DEFAULT_OUTPUT_FORMAT,
    style: str = DEFAULT_PLOT_STYLE,
):
    """Creates a multiline chart using different dataframe
    splits in the `ggplot` style."""
    with plt.style.context(style):
        plt.figure()
        ax = plt.axes()

        # Creates  splits.
        splits = df[split_key].unique()
        for split in splits:
            sub_df = df[df[split_key] == split]

            # Plots line.
            label = build_split_label(split)
            ax.plot(sub_df[x_key], sub_df[y_key], label=label)

            # Plots std.
            if not y_std_key is None:
                if y_std_key in sub_df.columns:
                    std = sub_df[y_std_key]
                else:
                    std = 0
                upper = sub_df[y_key].add(std)
                lower = sub_df[y_key].subtract(std)
                ax.fill_between(sub_df[x_key], upper, lower, alpha=0.25)

        ax.set_ylabel(y_label)
        ax.set_xlabel(x_label)

        # Sets legend
        if legend_position is None:
            ax.legend()
        else:
            ax.legend(loc=legend_position[0], bbox_to_anchor=legend_position[1])

        __save_plot(figure_output_path, display_output, output_format)
