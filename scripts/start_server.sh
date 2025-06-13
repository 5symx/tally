#!/bin/bash

TALLY_SERVER_BIN=${HOME%%/}/tally/build/tally_server

if [[ ! -z "$TALLY_HOME" ]]; then
    TALLY_SERVER_BIN=${TALLY_HOME%%/}/build/tally_server
fi
echo $TALLY_SERVER_BIN
$TALLY_SERVER_BIN
