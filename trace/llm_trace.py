
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math
import sys
import os
import json
sys.path.append('python')

#from bench_utils.utils import write_json_to_file
#from bench_utils.trace import scale_azure_trace, generate_azure_trace_with_load, plot_server_trace


def write_json_to_file(_dict, f_name):

    indexed_dict = {str(i): value for i, value in enumerate(_dict.values(), 1)}

    # Ensure the output directory exists
    dir_path = os.path.dirname(f_name)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    # Write the new dictionary to the file
    with open(f_name, 'w') as f:
        json.dump(indexed_dict, f, indent=4)


def scale_azure_trace(trace_filename, start_day=3, end_day=4, scaled_dur_secs=600):

    df_traces = pd.read_csv(trace_filename, parse_dates=["TIMESTAMP"])

    df_traces["TIMESTAMP"] = pd.to_datetime(df_traces["TIMESTAMP"])

    first_time = df_traces["TIMESTAMP"].min()

    df_traces["duration_since_first"] = (df_traces["TIMESTAMP"] - first_time).dt.total_seconds()
    
    target_fn_arrival_ts = df_traces["duration_since_first"]
    print(len(target_fn_arrival_ts))
    print(type(target_fn_arrival_ts))

    # # filter timestamps based on days
    # start_ts = 10
    # end_ts = 10 + scaled_dur_secs

    # target_fn_arrival_ts = target_fn_arrival_ts[
    #                             (target_fn_arrival_ts >= start_ts) &
    #                             (target_fn_arrival_ts < end_ts)]

    first_ts = target_fn_arrival_ts.index[0]
    last_ts = target_fn_arrival_ts.index[-1]
    trace_dur = last_ts - first_ts

    # let trace start from zero
    target_fn_arrival_ts = target_fn_arrival_ts - first_ts

    # scale the trace to have duration `scaled_dur_secs`
    normalized_arrival_ts = target_fn_arrival_ts # * (scaled_dur_secs / trace_dur)

    arrivial_ts_list = normalized_arrival_ts.tolist()[1:]
    return arrivial_ts_list

def plot_server_trace(timestamps_dict, interval=5, output_file="azure_trace.png", server_throughput=None):
    """
    Plots the request rate for multiple functions on the same graph.

    Args:
        timestamps_dict (dict): A dictionary of arrival timestamps for each function.
        interval (int): The time interval for binning requests.
        output_file (str): The path to save the output plot.
        server_throughput (float, optional): A horizontal line representing server throughput.
    """
    plt.figure(figsize=(20, 6))

    for fn_name, timestamps in timestamps_dict.items():
        if not timestamps:
            continue

        last_ts = timestamps[-1]
        bins = np.arange(0, math.ceil(last_ts), interval)

        # Calculate request rate
        counts, edges = np.histogram(timestamps, bins=bins)
        bin_centers = edges[:-1] + (interval / 2)
        request_rate = counts / interval
        request_rate[request_rate == 0] = np.nan # Use NaN for empty intervals for cleaner plots

        plt.plot(bin_centers, request_rate, linestyle='-', alpha=0.8, label=fn_name)

    plt.xlabel('Timestamp (s)')
    plt.ylabel('Requests per Second')
    plt.title('Request Rate Over Time for Top 5 Functions')
    plt.grid(True)

    if server_throughput:
        plt.axhline(y=server_throughput, color='r', linestyle='--', label='Server Throughput')

    plt.legend()
    plt.savefig(output_file)
    print(f"\nPlot saved to {output_file}")


if __name__ == "__main__":
    trace_code_name = "AzureLLMInferenceTrace_code.csv"
    trace_conv_name = "AzureLLMInferenceTrace_conv.csv"
    
    # trace should be at most 600 seconds
    max_trace_span = 600

    target_loads = [0.25, 0.5, 0.75]

    # ========== For trace analysis ===============

    # # generate 1 day trace

    all_arrival_ts = {}

    all_arrival_ts["code"] = scale_azure_trace(trace_code_name ) #, start_day=3, end_day=4, scaled_dur_secs=600)
    all_arrival_ts["conv"] = scale_azure_trace(trace_conv_name) #, start_day=3, end_day=4, scaled_dur_secs=600)
    
    plot_server_trace(all_arrival_ts, interval=1, server_throughput=None, output_file="azure_trace_llm.png")
    write_json_to_file(all_arrival_ts, "azure_trace_for_llm.json")