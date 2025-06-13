# fit with L40S sm_89

## benchmark scripts/run_test

### naive cufunction

change get_candidate_cuda_compute_capabilities() list into "89"
./build/test/elementwise --pass 

### pytorch intercept
using start_client_local.sh in run_test.sh  avoid cuGetExportTable internal API runtime_error
