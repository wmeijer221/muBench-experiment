from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
import sched
import time
from TimingError import TimingError
import requests
import json
import sys
import os
import shutil
from pprint import pprint


RUNNER_PATH = os.path.dirname(__file__)

if len(sys.argv) > 1:
    parameters_file_path = sys.argv[1]
else:
    parameters_file_path = f'{RUNNER_PATH}/RunnerParameters.json'


last_print_time_ms = 0
requests_processed = 0


try:
    with open(parameters_file_path) as f:
        params = json.load(f)
    runner_parameters = params['RunnerParameters']
    ms_access_gateway = runner_parameters["ms_access_gateway"]
    workloads = runner_parameters["workload_files_path_list"]
    threads = runner_parameters["thread_pool_size"]
    round = runner_parameters["workload_rounds"]  # number of repetition rounds
    if "OutputPath" in params.keys() and len(params["OutputPath"]) > 0:
        output_path = params["OutputPath"]
        if output_path.endswith("/"):
            output_path = output_path[:-1]
        if not os.path.exists(output_path):
            os.makedirs(output_path)
    else:
        output_path = RUNNER_PATH

except Exception as err:
    print("ERROR: in Runner,", err)
    exit(1)

## Check if "workloads" is a directory path, if so take all the workload files inside it
if os.path.isdir(workloads[0]):
    dir_workloads = workloads[0]
    workloads = list()
    src_files = os.listdir(dir_workloads)
    for file_name in src_files:
        full_file_name = os.path.join(dir_workloads, file_name)
        if os.path.isfile(full_file_name):
            workloads.append(full_file_name)

stats = list()
start_time = 0.0

def do_requests(event, stats):
    global requests_processed, last_print_time_ms
    # pprint(workload[event]["services"])
    # for services in event["services"]:
        # print(services)
    requests_processed = requests_processed + 1    
    try:
        now_ms = time.time_ns() // 1_000_000
        r = requests.get(f"{ms_access_gateway}/{event['service']}")
        req_latency_ms = r.elapsed.total_seconds()*1000
        stats.append(f"{now_ms} \t {req_latency_ms}")
        if now_ms > last_print_time_ms + 10_000:
            print(f"Processed request {requests_processed}, latency {req_latency_ms} \n")
            last_print_time_ms = now_ms
 
        return event['time'], req_latency_ms
    except Exception as err:
        print("Error: %s" % err)


def job_assignment(v_pool, v_futures, event, stats):
    try:
        worker = v_pool.submit(do_requests, event, stats)
        # Wait for the thread state change
        time.sleep(0.0001)
        #  If thread status is PENDING i can not respect the timing requirements
        if worker._state == "PENDING":
            raise TimingError(event['time'])
        v_futures.append(worker)
    except TimingError as err:
        print("Error: %s" % err)


def runner(workload=None):
    global start_time, stats

    print("###############################################")
    print("############   Run Forrest Run!!   ############")
    print("###############################################")
    if len(sys.argv) > 1 and workload is None:
        workload_file = sys.argv[1]
    else:
        workload_file = workload

    with open(workload_file) as f:
        workload = json.load(f)
    s = sched.scheduler(time.time, time.sleep)
    pool = ThreadPoolExecutor(threads)
    futures = list()
    for event in workload:
        # in seconds
        # s.enter(event["time"], 1, job_assignment, argument=(pool, futures, event))
        # in milliseconds
        s.enter((event["time"]/1000+2), 1, job_assignment, argument=(pool, futures, event, stats))

    start_time = time.time()
    print("Start Time:", datetime.now().strftime("%H:%M:%S.%f - %g/%m/%Y"))
    s.run()

    wait(futures)
    print("###############################################")
    print("###########   Stop Forrest Stop!!   ###########")
    print("###############################################")
    print("Run Duration (sec): %.6f" % (time.time() - start_time))


if output_path != RUNNER_PATH:
    shutil.copy(parameters_file_path, f"{output_path}/")

for cnt, workload_var in enumerate(workloads):
    for x in range(round):
        print("Round: %d -- workload: %s" % (x+1, workload_var))
        runner(workload_var)
        print("***************************************")
    #     if cnt != len(workloads) - 1 or x != round - 1:
    #         print("Sleep for 240 sec")
    #         time.sleep(240)
    # if cnt != len(workloads) - 1:
    #     print("Sleep for 240 sec")
    #     time.sleep(240)
with open(f"{output_path}/result.txt", "w") as f:
    f.writelines("\n".join(stats))
