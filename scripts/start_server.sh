#!/bin/bash

TALLY_SERVER_BIN=${HOME%%/}/tally/build/tally_server

if [[ ! -z "$TALLY_HOME" ]]; then
    TALLY_SERVER_BIN=${TALLY_HOME%%/}/build/tally_server
fi
echo $TALLY_SERVER_BIN

if [[ "$1" == "profile" ]]; then
    echo "Launching Tally Server with nsys profile..."
    # nsys profile -o my_profile_report --delay 5 --duration 10 $TALLY_SERVER_BIN
    nsys profile --capture-range cudaProfilerApi --trace cuda,osrt,nvtx --stats=true --force-overwrite true $TALLY_SERVER_BIN
else
    echo "Launching Tally Server directly (without nsys profile)..."
    TALLY_REUSABLE_WINDOWS=1 $TALLY_SERVER_BIN
fi