#!/bin/bash

conv_number=$1

echo "executing 1b ... "
# Run the first script and log output
# sudo ./scripts/run_test.sh server_fr3 1 "$conv_number" 2>&1 | tee mps-con"$conv_number"-1b.log
sudo ./scripts/run_test.sh server_fr3 1 "$conv_number" 2>&1 | grep -v 'EOG' > mps-con${conv_number}-1b.log
sleep 3

# Check if 1.log exists before running the second
if [ -f "mps-con"$conv_number"-1b.log" ]; then
    echo "executing 4b ... "
    sudo ./scripts/run_test.sh server_fr3 4 "$conv_number" 2>&1 | grep -v 'EOG' > mps-con"$conv_number"-4b.log
else
    echo "mps-con"$conv_number"5-1b.log not found. Skipping second run."
fi

sleep 3

# Check if 1.log exists before running the second
if [ -f "mps-con"$conv_number"-4b.log" ]; then
    echo "executing 27b ... "
    sudo ./scripts/run_test.sh server_fr3 27 "$conv_number" 2>&1 | grep -v 'EOG' > mps-con"$conv_number"-27b.log
else
    echo "mps-con15-4b.log not found. Skipping second run."
fi

sleep 3

# # Check if 1.log exists before running the second
if [ -f "mps-con"$conv_number"-27b.log" ]; then
    echo "executing 12b ... "   
    sudo ./scripts/run_test.sh server_fr3 12 "$conv_number" 2>&1 | grep -v 'EOG' > mps-con"$conv_number"-12b.log
else
    echo "mps-con"$conv_number"-27b.log not found. Skipping second run."
fi