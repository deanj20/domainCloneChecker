#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <filename.db>"
    exit 1
fi

database="$1"
output="exported_${database%.*}.csv"

sqlite3 "$database" -csv -header "SELECT * FROM ${database%.*};" > "$output"

echo "Exported data to $output"

