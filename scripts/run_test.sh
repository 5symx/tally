#!/bin/bash

cleanup() {
    ./scripts/kill_server.sh
    ./scripts/kill_iox.sh
}

run_tally_test() {

    # Launch tally server in the background
    ./scripts/start_server.sh &

    sleep 5

    echo $@
    
    if [[ ! -z "$REPLACE_CUBLAS" ]]; then
        echo "Running with REPLACE_CUBLAS set ..."
    fi

    # Launch client process
    ./scripts/start_client.sh $@

    ./scripts/kill_server.sh
}

test_list=(
#    "python3 ./tests/pytorch_samples/addmm.py"
    "./build/tests/elementwise_no_ptx"
    "./build/tests/elementwise"
   # "./tests/cudnn_samples_v8/mnistCUDNN/mnistCUDNN"
)

# Set up
trap cleanup ERR
set -e

# Build tally and tests
make
#cd tests && cd cudnn_samples_v8 && make && cd .. && cd ..

./scripts/start_iox.sh &
sleep 5

# Run tests with tally-server-client
for item in "${test_list[@]}"; do
    run_tally_test $item
done

# Run tests again with REPLACE_CUBLAS set
for item in "${test_list[@]}"; do
    REPLACE_CUBLAS=TRUE run_tally_test $item
done

cleanup

echo All tests passed!

rm result.txt 2> /dev/null
