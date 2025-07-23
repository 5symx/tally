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
   


def scale_azure_trace(trace_file_name, start_day=3, end_day=4, scaled_dur_secs=3600):
    """
    Processes an Azure trace file to extract and scale the arrival timestamps
    for the top 5 most frequent functions.

    Returns:
        dict: A dictionary where keys are function names and values are the
              scaled arrival timestamp lists.
    """
    trace_df = pd.read_csv(trace_file_name)

    top_n = 3

    # Get the top 5 most frequent functions
    fn_count = trace_df['func'].value_counts(ascending=False)
    top_n_fns = fn_count.head(top_n)
    print("Top 5 most frequent functions:")
    print(top_n_fns)

    all_arrival_ts = {}

    for i in range(top_n):
        if i == 1 or i == 3: # bypass 2 and 4 
            continue
        target_fn = top_n_fns.index[i]
        print(f"\nProcessing function {i+1}: {target_fn}")

        # Filter the DataFrame for the current target function
        target_fn_df = trace_df[trace_df["func"] == target_fn]

        # Calculate arrival timestamps
        target_fn_arrival_ts = (target_fn_df["end_timestamp"] - target_fn_df["duration"]).to_numpy()
        target_fn_arrival_ts.sort()
        print(f"  Total arrivals: {len(target_fn_arrival_ts)}")

        # Filter timestamps by day
        start_ts = start_day * 3600 * 24
        end_ts = end_day * 3600 * 24
        target_fn_arrival_ts = target_fn_arrival_ts[
            (target_fn_arrival_ts >= start_ts) & (target_fn_arrival_ts < end_ts)
        ]
        print(f"  Arrivals within time window: {len(target_fn_arrival_ts)}")

        if len(target_fn_arrival_ts) < 2:
            print(f"  Skipping {target_fn} due to insufficient data in the time window.")
            continue

        # Normalize timestamps to start from zero
        first_ts = target_fn_arrival_ts[0]
        trace_dur = target_fn_arrival_ts[-1] - first_ts
        target_fn_arrival_ts = target_fn_arrival_ts - first_ts

        # Scale the trace duration
        if trace_dur > 0:
            normalized_arrival_ts = target_fn_arrival_ts * (scaled_dur_secs / trace_dur)
            all_arrival_ts[target_fn] = normalized_arrival_ts.tolist()[1:]
        else:
            print(f"  Skipping {target_fn} due to zero trace duration.")

    return all_arrival_ts

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
    trace_file_name = "AzureFunctionsInvocationTraceForTwoWeeksJan2021.txt"
    
    # trace should be at most 600 seconds
    max_trace_span = 600

    target_loads = [0.25, 0.5, 0.75]

    # ========== For trace analysis ===============

    # # generate 1 day trace
    generated_trace = scale_azure_trace(trace_file_name, start_day=3, end_day=4, scaled_dur_secs=600)
    plot_server_trace(generated_trace, interval=1, server_throughput=250, output_file="azure_trace_one_day.png")
    write_json_to_file(generated_trace, "azure_trace_for_one_day.json")

    # generate 2 week trace
    # generated_trace = scale_azure_trace(trace_file_name, start_day=0, end_day=14, scaled_dur_secs=600 * 14)
    # plot_server_trace(generated_trace, interval=1, server_throughput=250, output_file="azure_trace_two_week.png")
    # write_json_to_file(generated_trace, "infer_trace/azure_trace_for_bert_two_week.json")

    # ========== For traffic load analysis ===============
    
    # single_job_df = pd.read_csv("tally_results/single-job-perf.csv")
    # single_job_df = single_job_df[single_job_df["workload_type"] == "inference-single-stream"]
    # inference_jobs = single_job_df["exp_key"].unique()
    # for inference_job in inference_jobs:

    #     inference_job_name = inference_job.replace("_infer_single-stream_1", "")
    #     req_latency_ms = single_job_df[single_job_df["exp_key"] == inference_job]["original_avg_latency"].values[0]
    #     req_latency_s = req_latency_ms / 1000

    #     for load in target_loads:
    #         generated_trace = generate_azure_trace_with_load(trace_file_name, req_latency_s, max_trace_span, start_day=3, end_day=4, target_load=load)
    #         write_json_to_file(generated_trace, f"infer_trace/azure_trace_{inference_job_name}_load_{load}.json")
