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
