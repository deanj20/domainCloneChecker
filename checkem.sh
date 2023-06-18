#!/bin/bash

domain_list="domains.txt"

while read line 
do
    name=$line
    echo "Looking up ${line}..."
    whois $name > ${line}.txt
    sleep 1
done < $domain_list
