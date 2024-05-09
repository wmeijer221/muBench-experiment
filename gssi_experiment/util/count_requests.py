import os
import itertools

from gssi_experiment.util.util import iterate_through_nested_folders


exp_name = "pinciroli_replication_fin/"

ga_folder = os.path.abspath(f"./gssi_experiment/gateway_aggregator/results/{exp_name}")
go_folder = os.path.abspath(f"./gssi_experiment/gateway_offloading/results/{exp_name}")
pnfj_folder = os.path.abspath(
    f"./gssi_experiment/pipes_and_filters/pipes_and_filters_joint/results/{exp_name}"
)
pnfs_folder = os.path.abspath(
    f"./gssi_experiment/pipes_and_filters/pipes_and_filters_separated/results/{exp_name}"
)

experiment_folders = itertools.chain(
    iterate_through_nested_folders(ga_folder, max_depth=2),
    iterate_through_nested_folders(go_folder, max_depth=3),
    iterate_through_nested_folders(pnfj_folder, max_depth=3),
    iterate_through_nested_folders(pnfs_folder, max_depth=3),
)

all_lines_counts = []
for experiment_folder in experiment_folders:
    print(experiment_folder)

    mubench_results_path = f"{experiment_folder}/mubench_results.csv"
    with open(mubench_results_path, "r", encoding="utf-8") as input_file:
        line_count = len(input_file.readlines())
        all_lines_counts.append(line_count)

min_x = min(all_lines_counts)
max_x = max(all_lines_counts)
avg_x = sum(all_lines_counts) / len(all_lines_counts)
print(f"{min_x=}, {max_x=}, {avg_x=}")
