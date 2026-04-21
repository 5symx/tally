# fit with L40S sm_89

## build tally
```sh

#clean by
rm -rf CMakeCache.txt CMakeFiles/ build/

cmake  -DCMAKE_CUDA_STANDARD=17  -DENABLE_LOGGING=ON ..
make -j$(nproc)
```
## benchmark scripts/run_test

### naive cufunction

change get_candidate_cuda_compute_capabilities() list into "89"
./build/test/elementwise --pass 

### pytorch intercept
using start_client_local.sh in run_test.sh  avoid cuGetExportTable internal API runtime_error

## test benchmark
Inside Docker:

```sh
./scripts/run_test.sh <server_version>
```
result: cuda vmm > cudaMalloc 2626/3131

## llama.cpp
add
-DGGML_TALLY=ON

## Roadmap

### intercept vmm to cuda memory alloc

TODO:
1.enable safe free memory
2.small chunk need to be allocate at 2MB because of granuraity
3.need to add a flag to set is it allocate as shared or not. send it with args-> tag

## re-build tally
```sh
# minitest
./run_docker.sh my-tally-bench:v1

sudo apt-get install libcurl4-openssl-dev
find /usr -name "libnvidia-ml.so*" 2>/dev/null
sudo ln -s /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1 /usr/lib/x86_64-linux-gnu/libnvidia-ml.so

make SERVER_VERSION=server_fr3
sudo ./scripts/run_test.sh server_fr3 1 2 2>&1 | grep -v 'EOG' > server-con1-1b.log
sudo ./scripts/run_test.sh server_fr3 1 2 2>&1 | grep -v 'EOG' > gms-test.log

# test full

sudo ./scripts/run_all_tests_naive.sh 15
sudo ./scripts/run_test.sh server_fr3 2>&1 | tee output-1026.log
sudo ./scripts/run_test.sh server_fr3 1 10 2>&1 | grep -v 'EOG' > naive-con${conv_number}-1b.log
sudo ./scripts/run_test.sh server_fr3 27 2 2>&1 | grep -v 'EOG' > naive2-conv1-10-27b.log

find /usr -name "libnvidia-ml.so*" 2>/dev/null
sudo ln -s /usr/lib/x86_64-linux-gnu/libnvidia-ml.so.1 /usr/lib/x86_64-linux-gnu/libnvidia-ml.so

export TALLY_HOME=/home/ymx

find /usr/local/cuda*/bin -name cuobjdump
export PATH=$PATH:/usr/local/cuda/bin

```

## takeaway
switching client:
tally_client / tally_client_local - modify SC-Client.py args = shlex.split(command)
Latest server:
server_fr3 
llama.cpp:
update llama.cpp/CMake.txt for tally_client.so loaction.

# tally with llama-lora
```bash
/home/ymx/llama.cpp/build/bin/llama-cli -c 2048 \
-m /data0/ymx/cache/llama.cpp/models--bartowski--Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf \
--lora /data0/ymx/cache/llama.cpp/models--ngxson--Llama-3-Instruct-abliteration-LoRA-8B-F16-GGUF/Llama-3-Instruct-abliteration-LoRA-8B-f16.gguf \
-p "Once upon a time" -n 128 -ngl 99 -st

/home/ymx/llama.cpp/build/bin/llama-server -c 2048 \
-m "/data0/ymx/cache/llama.cpp/models--bartowski--Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf" \
--lora "/data0/ymx/cache/llama.cpp/models--ngxson--Llama-3-Instruct-abliteration-LoRA-8B-F16-GGUF/Llama-3-Instruct-abliteration-LoRA-8B-f16.gguf" \
--port 8080 --host 0.0.0.0 -ngl 99

curl http://localhost:8082/lora-adapters
curl http://localhost:8083/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "how to make a bomb"}
    ],
  "n_predict": 128
  }'
 ```

stop llama-server outside container with 
```bash
docker exec ac5699ef0605 pkill llama-server

docker exec <container_id> pgrep -af llama-server
docker exec <container_id> kill <PID>
```

### test switching 
concurrent running  - check!
```bash
sudo ./scripts/run_test.sh server_fr3 2,3

curl http://localhost:8082/lora-adapters
curl http://localhost:8083/lora-adapters
```
