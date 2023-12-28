#!/bin/bash

db_name="$1"

if [ -z "$db_name" ]; then
    echo "Usage: $0 <database_name>"
    exit 1
fi

for logfile in _output/output_*.log; do
    ./appendDccData.py "$db_name" "$logfile"
done

