import subprocess
import time
import argparse

MODEL_NAME_TO_ID = {
    "ggml-org_gemma-3-1b-it-GGUF_gemma-3-1b-it-Q4_K_M.gguf": 1,
    "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf": 2,
    "lora-Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf": 3,
}

# Unique port mapping per model ID.
MODEL_ID_TO_PORT = {
    1: 8081,
    2: 8082,
    3: 8083,
}

def port_for_model_id(model_id: int) -> str:
    return str(MODEL_ID_TO_PORT.get(model_id, 9000 + model_id))


def parse_ids(id_args):
    ids = set()
    for raw in id_args:
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            ids.add(int(part))
    return ids

# (model_id, argv, sleep_duration_sec)
trace = [
    (
        MODEL_NAME_TO_ID["ggml-org_gemma-3-1b-it-GGUF_gemma-3-1b-it-Q4_K_M.gguf"],
        [
            "/home/ymx/llama.cpp/build/bin/llama-server",
            "-c", "2048",
            "-m", "/data0/ymx/cache/llama.cpp/ggml-org_gemma-3-1b-it-GGUF_gemma-3-1b-it-Q4_K_M.gguf",
            "--port", port_for_model_id(MODEL_NAME_TO_ID["ggml-org_gemma-3-1b-it-GGUF_gemma-3-1b-it-Q4_K_M.gguf"]),
            "--host", "0.0.0.0",
            "-ngl", "99",
        ],
        1,
    ),
    (
        MODEL_NAME_TO_ID["lora-Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"],
        [
            "/home/ymx/llama.cpp/build/bin/llama-server",
            "-c", "2048",
            "-m", "/data0/ymx/cache/llama.cpp/models--bartowski--Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
            "--lora", "/data0/ymx/cache/llama.cpp/models--ngxson--Llama-3-Instruct-abliteration-LoRA-8B-F16-GGUF/Llama-3-Instruct-abliteration-LoRA-8B-f16.gguf",
            "--port", port_for_model_id(MODEL_NAME_TO_ID["lora-Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"]),
            "--host", "0.0.0.0",
            "-ngl", "99",
        ],
        1,
    ),
    (
        MODEL_NAME_TO_ID["Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"],
        [
            "/home/ymx/llama.cpp/build/bin/llama-server",
            "-c", "2048",
            "-m", "/data0/ymx/cache/llama.cpp/models--bartowski--Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
            "--port", port_for_model_id(MODEL_NAME_TO_ID["Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"]),
            "--host", "0.0.0.0",
            "-ngl", "99",
        ],
        1,
    ),
]

def client(trace, selected_ids, backend):
    """
    Executes a trace of commands, launching each one in the background
    and then sleeping for the specified duration before launching the next.
    """
    print("Starting trace replay...")
    print(f"backend is {backend}")
    
    # Keep track of the processes we start
    processes = []

    selected_entries = [entry for entry in trace if entry[0] in selected_ids]
    missing_ids = sorted(selected_ids.difference({entry[0] for entry in trace}))
    if missing_ids:
        print(f"Warning: no trace entry found for id(s): {missing_ids}")

    if not selected_entries:
        print("No matching trace entries to run. Exiting.")
        return

    # for i in range(0, conv):  # 10
    print(f"launching {len(selected_entries)} command(s) concurrently")
    round_sleep = 0

    for model_id, command_argv, sleep_duration in selected_entries:
        print(f"--> [id={model_id}] Executing command: {' '.join(command_argv)}")

        if backend == "gms":
            # Align with run_test.sh style:
            # ./scripts/start_client.sh "${LLAMA_CMD_server[@]}"
            args = ['./scripts/start_client.sh', *command_argv]
        else:
            args = command_argv

        process = subprocess.Popen(args)
        processes.append(process)
        # round_sleep = max(round_sleep, sleep_duration)

        # if round_sleep > 0:
        #     print(f"    ...sleeping for {round_sleep} second(s).")
        #     time.sleep(round_sleep)

    print("\nTrace sequence launched. Waiting for all background processes to complete...")

    # Optionally, wait for all launched processes to finish
    for p in processes:
        p.wait()

    print("All trace processes have finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--id",
        action="append",
        required=True,
        help="Model id(s). Use comma-separated values (e.g. --id 2,3) or repeat (e.g. --id 2 --id 3).",
    )
    # parser.add_argument("--conv", type=int, required=True, help="conv number")
    parser.add_argument("--backend", type=str, required=True, help="backend choose from [gms, naive]")
    args = parser.parse_args()
    selected_ids = parse_ids(args.id)
    # conv = args.conv
    backend = args.backend

    client(trace, selected_ids, backend)
