#!/bin/bash

if [[ "$1" == "" || "$2" == "" || "$3" == "" ]]; then
    echo "Usage: $0 RESOLVER_ADDRESS domainlist.txt DNSTYPE"
    exit 1
fi

# output format: domain, rdata...

while read d; do
    a=`dig @$1 +short $3 $d`
    while read -r line; do
        d+=", $line"
    done <<< "$a"
    echo "$d"
done <"$2"
