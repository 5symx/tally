# fit with L40S sm_89

## build tally
```sh
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

## Roadmap

### intercept vmm to cuda memory alloc

TODO:
1.enable safe free memory
2.small chunk need to be allocate at 2MB because of granuraity
3.need to add a flag to set is it allocate as shared or not. send it with args-> tag

## re-build tally
```sh
./run_docker.sh my-tally-bench:v1

make SERVER_VERSION=server_fr3

sudo ./scripts/run_all_tests_naive.sh 15
sudo ./scripts/run_test.sh server_fr3 2>&1 | tee output-1026.log

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
