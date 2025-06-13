# fit with L40S sm_89
change get_candidate_cuda_compute_capabilities() list into "89"
./build/test/elementwise --pass

python ./build/test error 
