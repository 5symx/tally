import subprocess
import time
import random
import json
import statistics

# --- Sample Trace Data ---

# 1. For "azure" mode: A list of dictionaries.
# Each timestamp is in milliseconds, simulating what you'd get from a real trace.
# NOTE: These must be sorted by timestamp for the logic to work correctly.
# azure_trace_data = [
#     {
#         "command": "/home/ymx/tally/build/tests/elementwise",
#         "timestamp_s": 1614556801000  # Represents a specific point in time
#     },
#     {
#         "command": '/home/ymx/llama.cpp/build/bin/llama-simple -m /home/ymx/.cache/llama.cpp/ggml-org_gemma-3-4b-it-GGUF_gemma-3-4b-it-Q4_K_M.gguf -ngl 99 "once upon a time"',
#         "timestamp_s": 1614556804500  # 3.5 seconds after the first command
#     },
#     {
#         "command": "/home/ymx/tally/build/tests/elementwise",
#         "timestamp_s": 1614556804750  # 0.25 seconds after the second command
#     }
# ]




def generate_trace_from_json(commands_list, timestamps_json_file):
    """
    Merges a list of commands with a JSON file of timestamps to create
    a flat list of trace events.

    Args:
        commands_list (list): A list of command dictionaries, each with 'command_id' and 'command'.
        timestamps_json_file (str): The path to the JSON file with arrival timestamps.

    Returns:
        list: A sorted list of trace event dictionaries, ready for simulation.
    """
    # --- 1. Load the timestamps from the JSON file ---
    with open(timestamps_json_file, 'r') as f:
        timestamps_data = json.load(f)
    print(f"Loaded timestamps for {len(timestamps_data)} commands from '{timestamps_json_file}'")

    # --- 2. Create a command lookup dictionary for fast access ---
    # This maps command_id (int) to the command string.
    command_lookup = {cmd['command_id']: cmd['command'] for cmd in commands_list}

    # --- 3. Generate the flat list of all events ---
    all_trace_events = []
    for cmd_id_str, timestamps in timestamps_data.items():
        cmd_id_int = int(cmd_id_str)
        
        # Find the command string from our lookup
        if cmd_id_int not in command_lookup:
            print(f"Warning: Timestamps found for command_id '{cmd_id_int}', but no command was provided. Skipping.")
            continue
            
        command_str = command_lookup[cmd_id_int]
        
        # For each timestamp, create a new event record
        for ts_in_seconds in timestamps:
            # The simulation expects 'timestamp_s', so we convert seconds to milliseconds
            
            all_trace_events.append({
                'command': command_str,
                'timestamp_s': ts_in_seconds,
                'command_id': cmd_id_int # Keep the ID for potential future use
            })

    print(f"Generated a total of {len(all_trace_events)} trace events.")
    
    # --- 4. Sort the final list by timestamp ---
    # This is the critical step to prepare the data for the simulation loop.
    # sorted_trace = sorted(all_trace_events, key=lambda x: x['timestamp_s'])
    
    return all_trace_events



def trace_replayer(trace_data, mode='sequential', avg_interarrival_sec=2.0, trace_len=10):
    """
    Executes a trace of commands sequentially using different timing models.

    Args:
        trace_data: The list of commands and timing data.
        mode (str): The timing model to use. Can be:
                    'azure' -> Replays based on timestamps from the trace.
                    'poisson' -> Inter-arrival times follow a Poisson process.
                    'sequential' -> Uses the fixed sleep time from the trace tuple.
        avg_interarrival_sec (float): The average time between launches, used
                                      only in 'poisson' mode.
    """
    print(f"\n--- Starting trace replay in '{mode.upper()}' mode ---")

    latencies = []

    server_free_at = 0.0  # Tracks the time when the server becomes free (our virtual clock)
    current_arrival_time = 0.0 # Tracks the arrival time of requests


    if not trace_data:
        print("Trace data is empty. Nothing to do.")
        return

    if mode == 'azure':
        # Ensure data is sorted by timestamp, which is critical.

        filtered_events = [
            event for event in trace_data if event['timestamp_s'] < 10
        ]

        sorted_trace = sorted(filtered_events, key=lambda x: x['timestamp_s'])
        
        # last_launch_time_ms = sorted_trace[0]['timestamp_s']

        for i, item in enumerate(sorted_trace):
            command = item['command']
            
            current_arrival_time = item['timestamp_s']

            
            print(f"--> Request for '{command}' arrives at: {current_arrival_time:.4f}s")

            start_of_service_time = max(current_arrival_time, server_free_at)
            
            # The time this request had to wait in the queue
            wait_latency = start_of_service_time - current_arrival_time
            if wait_latency > 0.0001: # Add a small tolerance for floating point math
                print(f"  Server busy. Waited in queue for: {wait_latency:.4f}s")


            print(f"--> Launching: {command}")
            exe_latency = random.uniform(0.5, 1.5) # run_command(command)

            if exe_latency is not None:
                # The command is finished at the time it started plus its execution time
                completion_time = start_of_service_time + exe_latency
                
                # The total latency is the full duration from arrival to completion
                total_latency = completion_time - current_arrival_time
                latencies.append(total_latency)
                
                # The server is now busy until this command completes
                server_free_at = completion_time
                
                print(f"    Request completed at: {completion_time:.4f}s. Total latency: {total_latency:.4f}s")
                print("-" * 40)

    elif mode == 'poisson':
        
        if avg_interarrival_sec <= 0:
            print("ERROR: Average inter-arrival time must be positive for Poisson mode.")
            return
            
        # The rate (lambda) is 1 / average_time_between_events
        rate_lambda = 1.0 / avg_interarrival_sec

        print(f"Simulating Poisson arrivals with an average inter-arrival time of {avg_interarrival_sec:.4f}s (Rate λ = {rate_lambda:.2f} req/s)")
        print("-" * 40)
        
        for i, (command, _) in enumerate(trace_data):
            if i > 0:
                # Get the next sleep time from an exponential distribution
                inter_arrival_time = random.expovariate(rate_lambda)
                current_arrival_time += inter_arrival_time
            print(f"--> Request for '{command}' arrives at: {current_arrival_time:.4f}s")

            # The server can only start this command *after* it has arrived AND *after* it has finished the previous one.
            start_of_service_time = max(current_arrival_time, server_free_at)
            
            # The time this request had to wait in the queue
            wait_latency = start_of_service_time - current_arrival_time
            if wait_latency > 0.0001: # Add a small tolerance for floating point math
                print(f"  Server busy. Waited in queue for: {wait_latency:.4f}s")


            print(f"--> Launching: {command}")
            exe_latency = 1 #run_command(command)

            if exe_latency is not None:
                # The command is finished at the time it started plus its execution time
                completion_time = start_of_service_time + exe_latency
                
                # The total latency is the full duration from arrival to completion
                total_latency = completion_time - current_arrival_time
                latencies.append(total_latency)
                
                # The server is now busy until this command completes
                server_free_at = completion_time
                
                print(f"    Request completed at: {completion_time:.4f}s. Total latency: {total_latency:.4f}s")
                print("-" * 40)

    elif mode == 'sequential':
        for i, (command, sleep_duration) in enumerate(trace_data):
            if i > 0:
                inter_arrival_time = sleep_duration
                current_arrival_time += inter_arrival_time

            print(f"--> Request for '{command}' arrives at: {current_arrival_time:.4f}s")

            # The server can only start this command *after* it has arrived AND *after* it has finished the previous one.
            start_of_service_time = max(current_arrival_time, server_free_at)
            
            # The time this request had to wait in the queue
            wait_latency = start_of_service_time - current_arrival_time
            if wait_latency > 0.0001: # Add a small tolerance for floating point math
                print(f"    Server busy. Waited in queue for: {wait_latency:.4f}s")

            print(f"--> Launching  (and waiting): {command}")
            exe_latency = run_command(command)

            if exe_latency is not None:
                # The command is finished at the time it started plus its execution time
                completion_time = start_of_service_time + exe_latency
                
                # The total latency is the full duration from arrival to completion
                total_latency = completion_time - current_arrival_time
                latencies.append(total_latency)
                
                # The server is now busy until this command completes
                server_free_at = completion_time
                
                print(f"    Request completed at: {completion_time:.4f}s. Total latency: {total_latency:.4f}s")
                print("-" * 40)
            
    else:
        print(f"ERROR: Unknown mode '{mode}'")

     # --- Latency Report ---
    print(f"\n--- Latency Report for '{mode.upper()}' mode ---")
    if latencies:
        print(f"Total commands executed successfully: {len(latencies)}")
        print(f"Average Latency: {statistics.mean(latencies):.4f} seconds")
        print(f"Min Latency (fastest):   {min(latencies):.4f} seconds")
        print(f"Max Latency (slowest):    {max(latencies):.4f} seconds")
        # The 95th percentile is a very common and useful metric
        if len(latencies) > 1:
             p90 = statistics.quantiles(latencies, n=10)[8]
             print(f"95th Percentile Latency: {p90:.4f} seconds")
    else:
        print("No commands were successfully executed to generate a latency report.")


    print(f"--- Finished '{mode.upper()}' mode replay ---")


def run_command(command):
    """A helper function to run a command via the shell script."""
    try:
        args = ['./scripts/start_client.sh', command]
        
        # 1. Record start time
        start_time = time.monotonic()

        # subprocess.run is a blocking call. It waits for the command to finish.
        subprocess.run(args, check=True, text=True, capture_output=True)

        # 3. Record end time
        end_time = time.monotonic()

        # 4. Calculate latency
        latency = end_time - start_time
        print(f"    SUCCESS: Command finished in {latency:.4f} seconds.")
        return latency

    except FileNotFoundError:
        print("\nERROR: './start_client.sh' not found. Please ensure it exists and is executable.")
        exit(1)
    except subprocess.CalledProcessError as e:
        print(f"    ERROR: Command failed with exit code {e.returncode}")
        print(f"    STDERR: {e.stderr}")
        return None


if __name__ == "__main__":

    mode = 'azure'
    if mode == 'azure':

        # Define your inputs
        commands_list = [
            {"command_id": 1, "command": "/home/ymx/tally/build/tests/elementwise"},
            {"command_id": 2, "command": "/home/ymx/llama.cpp/build/bin/llama-simple -m /home/ymx/.cache/llama.cpp/ggml-org_gemma-3-4b-it-GGUF_gemma-3-4b-it-Q4_K_M.gguf -ngl 99 \"once upon a time\""}
        ]
        timestamps_file = '/home/ymx/tally/trace/azure_trace_for_llm.json' # Make sure this file exists with the content from above

        # Generate the trace data
        azure_trace_data = generate_trace_from_json(commands_list, timestamps_file)

        # Now, 'trace_data' is in the exact format your simulation loop needs.
        # You can print it to see the result:
        print("\n--- Generated and Sorted Trace Data ---")
        for event in azure_trace_data:
            print(event)
            break

        # 2. For "poisson" and "sequential" modes: The original list of tuples is fine.
        # The number '3' will be used by 'sequential' but ignored by 'poisson'.
        

        # --- EXAMPLE 1: Replay using Azure Timestamps ---
        # Simulates the exact timing from a production trace.

        trace_replayer(azure_trace_data, mode=mode)
    else:


        # --- EXAMPLE 2: Replay using a Poisson Process ---
        simple_trace_data = [
            ("/home/ymx/tally/build/tests/elementwise", 3),
            ('/home/ymx/llama.cpp/build/bin/llama-simple -m /home/ymx/.cache/llama.cpp/ggml-org_gemma-3-4b-it-GGUF_gemma-3-4b-it-Q4_K_M.gguf -ngl 99 "once upon a time"', 0),
        ]

        
        # Launches commands with an *average* interval of 2.5 seconds.
        # The actual intervals will be random.
        trace_replayer(simple_trace_data, mode='poisson', avg_interarrival_sec=0.5, trace_len=10)
        
        # --- EXAMPLE 3: The original sequential replay ---
        # Launches, waits, then sleeps for the fixed time in the data.
        # trace_replayer(simple_trace_data, mode='sequential', trace_len=10)