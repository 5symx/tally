#!/bin/bash
SERVER_VERSION=$1
MODEL_ID=$2
# CONV_NUM=$3

# LLAMA_CPP_DIR=/home/llama.cpp

export CUDA_VISIBLE_DEVICES="0"
# export TALLY_HOME=/home/ymx/tally
export TALLY_HOME=/home/ymx/tally
export PATH=$PATH:/usr/local/cuda/bin
export XDG_CACHE_HOME=/home/.cache
export TMPDIR=/home/ymx/my_tmp

if [ -z "$SERVER_VERSION" ]; then
    echo "Error: SERVER_VERSION is not set!"
    echo "Usage: ./run_tests.sh <server_version>"
    exit 1
fi

cleanup() {
    ./scripts/kill_server.sh
    ./scripts/kill_iox.sh
    # rm -rf ~/.cache/tally/transform/*
}

LLAMA_CMD_simple=(
    "/home/ymx/llama.cpp/build/bin/llama-simple"
    "-m" "/data0/ymx/cache/llama.cpp/ggml-org_gemma-3-1b-it-GGUF_gemma-3-1b-it-Q4_K_M.gguf"
    "-ngl" "99"
    "once upon a time"
)

LLAMA_CMD_cli=(
    /home/ymx/llama.cpp/build/bin/llama-cli 
    -c 2048 
    -m "/data0/ymx/cache/llama.cpp/models--bartowski--Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf" 
    --lora "/data0/ymx/cache/llama.cpp/models--ngxson--Llama-3-Instruct-abliteration-LoRA-8B-F16-GGUF/Llama-3-Instruct-abliteration-LoRA-8B-f16.gguf" 
    -p "Once upon a time" 
    -n 128 
    -ngl 99 
    -st
)

LLAMA_CMD_server=(
    /home/ymx/llama.cpp/build/bin/llama-server
    -c 2048 
    -m "/data0/ymx/cache/llama.cpp/models--bartowski--Meta-Llama-3.1-8B-Instruct-GGUF/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf" 
    --lora "/data0/ymx/cache/llama.cpp/models--ngxson--Llama-3-Instruct-abliteration-LoRA-8B-F16-GGUF/Llama-3-Instruct-abliteration-LoRA-8B-f16.gguf" 
    --port 8080 
    --host 0.0.0.0
    -ngl 99
)

run_tally_test() {

    # Launch tally server in the background
    # ./scripts/start_server.sh profile &
    ./scripts/start_server.sh  &

    sleep 5

    echo $@
    
    if [[ ! -z "$REPLACE_CUBLAS" ]]; then
        echo "Running with REPLACE_CUBLAS set ..."
    fi

    # Launch client process

    # python3 ./scripts/SC-client.py --id $MODEL_ID --conv $CONV_NUM --backend "gms"

    python3 ./scripts/SC-client.py --id $MODEL_ID --backend "gms"

    # sleep 3

    # ./scripts/start_client.sh './build/tests/elementwise' # check

    # sleep 3

    # ./scripts/start_client.sh '/home/ymx/llama.cpp/build/bin/llama-simple -m /data0/ymx/cache/llama.cpp/ggml-org_gemma-3-1b-it-GGUF_gemma-3-1b-it-Q4_K_M.gguf -ngl 99 "once upon a time"'

    # ./scripts/start_client.sh "${LLAMA_CMD_server[@]}"

    sleep 3

    # ./scripts/start_client.sh "$@" #./build/tests/elementwise

    # # sleep 3

    # ./scripts/start_client.sh '/home/ymx/llama.cpp/build/bin/llama-simple -m /home/ymx/.cache/llama.cpp/ggml-org_gemma-3-4b-it-GGUF_gemma-3-4b-it-Q4_K_M.gguf -ngl 99 "once upon a time"'

    # sleep 3

    ./scripts/kill_server.sh
} 


run_naive_test() {

    sleep 5

    # Launch client process
    # for i in {0..9}; do
    #     python3 ./scripts/SC-client.py --size $MODEL_SIZE --conv $CONV_NUM
    # done

    python3 ./scripts/SC-client.py --id $MODEL_id --backend "naive"
    
    sleep 3
} 

test_list=(
#    "python3 ./tests/pytorch_samples/addmm.py"
#    "python3 ./tests/pytorch_samples/run-imagenet.py"
#    '/home/ymx/llama.cpp/build/bin/llama-simple -m /home/ymx/.cache/llama.cpp/ggml-org_gemma-3-1b-it-GGUF_gemma-3-1b-it-Q4_K_M.gguf -ngl 99 "once upon a time"'
    '/home/ymx/llama.cpp/build/bin/llama-simple -m /data0/ymx/cache/llama.cpp/ggml-org_gemma-3-1b-it-GGUF_gemma-3-1b-it-Q4_K_M.gguf -ngl 99 "once upon a time"'
#
#    '/home/ymx/llama.cpp/build/bin/llama-cli -m /home/ymx/.cache/llama.cpp/ggml-org_tinygemma3-GGUF_tinygemma3-Q8_0.gguf -ngl 99 -no-cnv --prompt "once upon a time" -n 100 '
    # "./build/tests/test_sync" 
#   "./build/tests/elementwise"
#    "./build/tests/cuda-memcpy-test"	# cuMemAlloc
#    "./build/tests/test-vmm"
#    "./build/tests/test-sync"  # microbench
   # "./tests/cudnn_samples_v8/mnistCUDNN/mnistCUDNN"
)

# Set up
trap cleanup ERR
set -e

apt-get install -y libcurl4-openssl-dev 

echo "Starting the make..."
# Build tally and tests
make SERVER_VERSION=$SERVER_VERSION

cd ../llama.cpp &&  \
cmake -B build \
      -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc \
      -DCUDAToolkit_ROOT=/usr/local/cuda \
      -DGGML_CUDA=ON \
      -DGGML_TALLY=ON \
      -DCMAKE_CUDA_ARCHITECTURES="86" \
      -DGGML_CUDA_NO_VMM=ON \
      -DGGML_CUDA_FORCE_CUBLAS=ON \
      -DGGML_CUDA_F16=ON \
      -DGGML_CUDA_FA=OFF \
      -DBUILD_SHARED_LIBS=1  \
      -DGGML_CUDA_GRAPHS=OFF && \
cmake --build build --config Release -j$(nproc) && \
cd ../tally


#cd tests && cd cudnn_samples_v8 && make && cd .. && cd ..


./scripts/kill_server.sh & 
sleep 5

./scripts/kill_iox.sh &
sleep 5

./scripts/start_iox.sh &
sleep 5

# Run tests with tally-server-client
# for item in "${test_list[@]}"; do
#     run_tally_test "$item"
# done

for i in {0..0}; do # 10
    run_tally_test 
done

# for i in {0..1}; do # 10
#     run_naive_test 
# done


# Run tests again with REPLACE_CUBLAS set
#for item in "${test_list[@]}"; do
#    REPLACE_CUBLAS=TRUE run_tally_test $item
#done

cleanup

echo All tests passed!

rm result.txt 2> /dev/null
