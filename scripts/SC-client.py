import subprocess
import time
import shlex
import argparse

# This would be the parsed data from your Azure trace
# (command, time_to_next_request_in_seconds)
trace = [
    # ("/home/ymx/tally/build/tests/elementwise", 3),
    (27,'/home/ymx/llama.cpp/build/bin/llama-simple -m /data0/ymx/cache/llama.cpp/ggml-org_gemma-3-27b-it-GGUF_gemma-3-27b-it-Q4_K_M.gguf -ngl 99 "once upon a time"', 1),
    (1,'/home/ymx/llama.cpp/build/bin/llama-simple -m /data0/ymx/cache/llama.cpp/ggml-org_gemma-3-1b-it-GGUF_gemma-3-1b-it-Q4_K_M.gguf -ngl 99 "once upon a time"',1),
    (12,'/home/ymx/llama.cpp/build/bin/llama-simple -m /data0/ymx/cache/llama.cpp/ggml-org_gemma-3-12b-it-GGUF_gemma-3-12b-it-Q4_K_M.gguf -ngl 99 "once upon a time"', 1),
    (4,'/home/ymx/llama.cpp/build/bin/llama-simple -m /data0/ymx/cache/llama.cpp/ggml-org_gemma-3-4b-it-GGUF_gemma-3-4b-it-Q4_K_M.gguf -ngl 99 "once upon a time"', 1),

    # ('/home/ymx/llama.cpp/build/bin/llama-simple -m /home/ymx/.cache/llama.cpp/ggml-org_gemma-3-12b-it-GGUF_gemma-3-12b-it-Q4_K_M.gguf -ngl 99 "once upon a time"', 1),
    # ("/home/ymx/tally/build/tests/elementwise", 3),
    # ('/home/ymx/llama.cpp/build/bin/llama-simple -m /home/ymx/.cache/llama.cpp/ggml-org_gemma-3-1b-it-GGUF_gemma-3-1b-it-Q4_K_M.gguf -ngl 99 "once upon a time"', 1),
    # ('/home/ymx/llama.cpp/build/bin/llama-simple -m /home/ymx/.cache/llama.cpp/ggml-org_gemma-3-4b-it-GGUF_gemma-3-4b-it-Q4_K_M.gguf -ngl 99 "once upon a time"', 1),
    
    # ('/home/ymx/llama.cpp/build/bin/llama-simple -m /home/ymx/.cache/llama.cpp/ggml-org_gemma-3-27b-it-GGUF_gemma-3-27b-it-Q4_K_M.gguf -ngl 99 "a long time ago"', 1),
    # ('/home/ymx/llama.cpp/build/bin/llama-simple -m /home/ymx/.cache/llama.cpp/ggml-org_gemma-3-1b-it-GGUF_gemma-3-1b-it-Q4_K_M.gguf -ngl 99 "once upon a time"', 1),
    # ('/home/ymx/llama.cpp/build/bin/llama-simple -m /home/ymx/.cache/llama.cpp/ggml-org_gemma-3-4b-it-GGUF_gemma-3-4b-it-Q4_K_M.gguf -ngl 99 "have a nice day"', 1),

    # ('/home/ymx/llama.cpp/build/bin/llama-simple -m /home/ymx/.cache/llama.cpp/ggml-org_Qwen2.5-VL-7B-Instruct-GGUF_Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf -ngl 99 "a long time ago"', 1),
    # ('/home/ymx/llama.cpp/build/bin/llama-simple -m /home/ymx/.cache/llama.cpp/ggml-org_Qwen2.5-VL-3B-Instruct-GGUF_Qwen2.5-VL-3B-Instruct-Q4_K_M.gguf -ngl 99 "a long time ago"', 1),
    # ('/home/ymx/llama.cpp/build/bin/llama-simple -m /home/ymx/.cache/llama.cpp/ggml-org_Qwen2.5-VL-32B-Instruct-GGUF_Qwen2.5-VL-32B-Instruct-Q4_K_M.gguf -ngl 99 "a long time ago"', 1),
    # ('/home/ymx/llama.cpp/build/bin/llama-simple -m /home/ymx/.cache/llama.cpp/ggml-org_Qwen2.5-VL-72B-Instruct-GGUF_Qwen2.5-VL-72B-Instruct-Q4_K_M.gguf -ngl 99 "a long time ago"', 1),
    
]

def client(trace, size, conv):
    """
    Executes a trace of commands, launching each one in the background
    and then sleeping for the specified duration before launching the next.
    """
    print("Starting trace replay...")
    
    # Keep track of the processes we start
    processes = []

    for i in range(0, conv): # 10

        for model_size, command, sleep_duration in trace:
            if model_size == size:
                print(f"--> Executing command: {command}")
                
                # We construct the command line to call our shell script.
                # The script name is the first part, and the command to run is the second.
                # This is robust and avoids shell injection issues.

                # args = ['./scripts/start_client.sh', command] # test for gm
                args = shlex.split(command)

                # subprocess.Popen launches the command in a new process
                # without blocking the execution of this script.
                process = subprocess.Popen(args)
                processes.append(process)

                # try:
                #     subprocess.run(args, check=True)
                #     print(f"    '{command}' finished successfully.")
                # except subprocess.CalledProcessError as e:
                #     print(f"    ERROR: Command failed with exit code {e.returncode}")

                
                if sleep_duration > 0:
                    print(f"    ...sleeping for {sleep_duration} second(s).")

                    time.sleep(0.5)

    print("\nTrace sequence launched. Waiting for all background processes to complete...")

    # Optionally, wait for all launched processes to finish
    for p in processes:
        p.wait()

    print("All trace processes have finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, required=True, help="Size parameter")
    parser.add_argument("--conv", type=int, required=True, help="conv number")
    args = parser.parse_args()
    size = args.size
    conv = args.conv

    client(trace, size, conv)
