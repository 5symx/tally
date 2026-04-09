#!/bin/bash

shopt -s expand_aliases
alias python3="python3.9"

TALLY_CACHE_PATH=${HOME%%/}/.cache/tally/.tally_cache
TALLY_CACHE_CLIENT_PATH=${HOME%%/}/.cache/tally/.tally_cache_client

TALLY_CLIENT_LIB=libtally_client.so

TALLY_CLIENT_LIB_PATH=${HOME%%/}/tally/build/$TALLY_CLIENT_LIB

if [[ ! -z "$TALLY_HOME" ]]; then
    TALLY_CLIENT_LIB_PATH=${TALLY_HOME%%/}/build/$TALLY_CLIENT_LIB
fi

# Copy cache if not already exists
if [ -e "$TALLY_CACHE_PATH" ]; then
    if [ -e "$TALLY_CACHE_CLIENT_PATH" ]; then
        if ! cmp -s "$TALLY_CACHE_PATH" "$TALLY_CACHE_CLIENT_PATH"; then
            cp $TALLY_CACHE_PATH $TALLY_CACHE_CLIENT_PATH
        fi
    else
        cp $TALLY_CACHE_PATH $TALLY_CACHE_CLIENT_PATH
    fi
fi

# OVERRIDE_PATH=${TALLY_HOME%%/}/build/liboverride.so

# LD_PRELOAD=$TALLY_CLIENT_LIB_PATH:$OVERRIDE_PATH $@

# echo "$TALLY_CLIENT_LIB_PATH"
# ls -l "$TALLY_CLIENT_LIB_PATH"
# ldd "$TALLY_CLIENT_LIB_PATH"

# LD_PRELOAD=$TALLY_CLIENT_LIB_PATH $@
LD_PRELOAD="$TALLY_CLIENT_LIB_PATH" "$@"