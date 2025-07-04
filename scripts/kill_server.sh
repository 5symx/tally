#!/bin/bash

# pid=$(ps -ef | grep tally_server | grep -v grep | awk '{print $2}')
pid=$(pgrep tally_server)

# kill -15 $pid > /dev/null 2>&1
kill -s SIGINT "$pid" > /dev/null 2>&1


if [ ! -z "$pid" ]
then
    while [ -e /proc/$pid ]
    do
    # while kill -0 "$pid" > /dev/null 2>&1; do
        sleep 0.1
    done
fi