from WorkLoadGenerator import get_workload, json, pprint


# INPUT params:
# ingress_list = {"s1": 1, "s2": 0.8, "s4": 0.5}
ingress_list = {"s0": 1}
request_parameters = {"stop_event": 100, "mean_interarrival_time": 300}

####################


# workload = get_workload(ingress_list, {"min": 1, "max": 3}, request_parameters)
workload = get_workload(ingress_list, {"min": 1, "max": 1}, request_parameters)
pprint(workload)

keyboard_input = input("Save work model on file? (y)") or "y"

if keyboard_input == "y":
    with open("workload.json", "w") as f:
        f.write(json.dumps(workload))


