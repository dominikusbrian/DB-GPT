from configs import POSTGRESQL_CONFIG
from multiagents.our_argparse import args
import warnings
from multiagents.tools.metrics import *
import numpy as np
from multiagents.utils.database import DBArgs, Database
import time
import json

# [anomaly script]

with open(args.anomaly_file, 'r') as f:
    anomalies_list = json.load(f)
    for i in anomalies_list:
        exceptions = {}

        if "exceptions" not in anomalies_list[i]:
            raise Exception(f"No metric values found for anomaly {i} in the file {args.anomaly_file}!")

        for c in anomalies_list[i]["exceptions"]:
            for k, v in anomalies_list[i]["exceptions"][c].items():
                if k not in exceptions:
                    exceptions[k] = v

        anomalies_list[i]["exceptions"] = exceptions

def update_current_time():
    current_diag_time = time.localtime()
    current_diag_time = time.strftime("%Y-%m-%d-%H:%M:%S", current_diag_time)

    return current_diag_time


current_diag_time = update_current_time()

# [index advisor]
advisor = "db2advis"  # option: extend, db2advis (fast)

# [workload statistics]
dbargs = DBArgs("postgresql", config=POSTGRESQL_CONFIG)
db = Database(dbargs, timeout=-1)
WORKLOAD_FILE_NAME = "workload_info.json"


def get_workload_statistics():
    with open(WORKLOAD_FILE_NAME, 'r') as f:
        info = json.load(f)
        return info["workload_statistics"]


def get_slow_queries(diag_id):
    with open(args.anomaly_file, 'r') as f:
        info = json.load(f)
    return info[diag_id]["slow_queries"]


def get_workload_sqls(diag_id):
    with open(args.anomaly_file, 'r') as f:
        info = json.load(f)
    return info[diag_id]["workload"]


# [functions]
def obtain_values_of_metrics(i, metrics, start_time, end_time):
    required_values = {}

    for metric in metrics:
        match_metric = metric.split("{")[0]
        if match_metric in anomalies_list[i]["exceptions"]:
            required_values[match_metric] = anomalies_list[i]["exceptions"][match_metric]
        else:
            # print(colored(f"No metric values found for {start_time}-{end_time} of {metric}", "red"))
            pass

    return required_values


def processed_values(data):
    if data == []:
        raise Exception("No metric values found for the given time range")

    # compute processed values for the metric
    # max (reserve two decimal places)
    max_value = round(np.max(np.array(data)), 2)
    # min
    min_value = round(np.min(np.array(data)), 2)
    # mean
    mean_value = round(np.mean(np.array(data)), 2)
    # deviation
    deviation_value = round(np.std(np.array(data)), 2)
    # evenly sampled 10 values (reserve two decimal places)
    evenly_sampled_values = [round(data[i], 2) for i in range(0, len(data), len(data) // 10)]

    # describe the above five values in a string
    return f"the max value is {max_value}, the min value is {min_value}, the mean value is {mean_value}, the deviation value is {deviation_value}, and the evenly_sampled_values are {evenly_sampled_values}."
