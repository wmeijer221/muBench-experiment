from subprocess import Popen

import matplotlib.pyplot as plt
import numpy as np

from os import removedirs, remove


temp_worker_param_path = "./gssi_experiment/gateway_aggregator/tmp_work_model.json"

base_worker_param = """{{
   "RunnerParameters": {{
      "ms_access_gateway": "http://192.168.49.2:31113",
      "workload_files_path_list": [
         "SimulationWorkspace/workload.json"
      ],
      "workload_rounds": 1,
      "workload_type": "greedy",
      "workload_events": 5000,
      "thread_pool_size": 8,
      "result_file": "result",
      "HeaderParameters": {{
         "type": "AggregatedHeaderFactory",
         "parameters": {{
            "base_endpoint": "http://192.168.49.2:31113/",
            "endpoints": [
               "s1",
               "s2",
               "s3"
            ],
            "probabilities": [
               {s1_intensity},
               1,
               {s3_intensity}
            ]
         }}
      }}
   }},
   "OutputPath": "SimulationWorkspace/Result",
   "_AfterWorkloadFunction": {{
      "_comment": "remove _ from the object name to execute the funcions",
      "file_path": "Function",
      "function_name": "get_prometheus_stats"
   }}
}}
"""


steps = 20
step_size = 1.0 / steps


experimental_results = []


for i in range(steps + 1):
    # 1: prepares the experiment.
    s1_intensity = i * step_size

    experiment_params = base_worker_param.format(
        s1_intensity=s1_intensity, s3_intensity=1 - s1_intensity
    )

    with open(temp_worker_param_path, mode="w+", encoding="utf-8") as temp_work_params:
        print(
            f"experiment-{i + 1}/{steps + 1}: {s1_intensity=}, {temp_work_params.name=}"
        )
        temp_work_params.write(experiment_params)
        print(experiment_params)

    # 2: runs the experiment.
    args = [
        "./gssi_experiment/run-full-experiment.sh",
        "./gssi_experiment/gateway_aggregator/K8sParameters.json",
        temp_work_params.name,
    ]
    print(args)
    proc = Popen(args)
    proc.wait()

    # 3: processes the results.
    with open(
        "./SimulationWorkspace/Result/result.txt", "r", encoding="utf-8"
    ) as results_file:
        delays = []
        for entry in results_file:
            elements = entry.split()
            delay = int(elements[1])
            delays.append(delay)
        mn = np.min(delays)
        mx = np.max(delays)
        avg = np.average(delays)
        std = np.std(delays)
        print(f"{s1_intensity=}: {mn=}, {mx=}, {avg=}, {std=}")

        experimental_results.append((s1_intensity, mn, mx, avg, std))

# Dummy data
# experimental_results = [
#     (0.4, 63, 1129, 312.7676,143.06962078037392),
#     (0.6, 63, 1045, 295.2754, 133.2716202154082),
#     (0.8, 57,  1132,  296.3602, 140.70607256248752)
# ]

print(experimental_results)

# 4: plots the results
x = [point[0] for point in experimental_results]
y_min = [point[1] for point in experimental_results]
y_max = [point[2] for point in experimental_results]
y_avg = [point[3] for point in experimental_results]
std_dev = [point[4] for point in experimental_results]

# Creating the line chart
plt.figure(figsize=(10, 6))
plt.plot(x, y_min, label="Min")
plt.plot(x, y_max, label="Max")
plt.plot(x, y_avg, label="Average")

# Creating the area around the average line for the standard deviation
plt.fill_between(
    x,
    np.subtract(y_avg, std_dev),
    np.add(y_avg, std_dev),
    color="b",
    alpha=0.2,
    label="Standard Deviation",
)

# Adding labels and title
plt.xlabel("S1 Intensity")
plt.ylabel("Delay (ms)")
plt.title("Differences in delay for different values of S1 Intensity.")
plt.legend()
plt.grid(True)
# plt.show()
plt.savefig("./gssi_experiment/gateway_aggregator/figure.png")


# 5: cleanup
remove(temp_worker_param_path)
