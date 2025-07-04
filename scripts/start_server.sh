#!/bin/bash

TALLY_SERVER_BIN=${HOME%%/}/tally/build/tally_server

if [[ ! -z "$TALLY_HOME" ]]; then
    TALLY_SERVER_BIN=${TALLY_HOME%%/}/build/tally_server
fi
echo $TALLY_SERVER_BIN
# nsys profile -o my_profile_report --delay 5 --duration 10 $TALLY_SERVER_BIN
nsys profile --capture-range cudaProfilerApi --trace cuda,osrt,nvtx  --force-overwrite true $TALLY_SERVER_BIN
# $TALLY_SERVER_BIN