**dnsfastquery is a Python tool for sending DNS queries to a bulk domain list for research purposes.**

## Use Case

One way to send DNS queries for a bulk domain list is to call `dig` or `drill` in a script. Example:

```bash
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
```

This works well for up to a couple of thousand domains, but may be too slow for more than that. Evaluation of the output may become difficult, depending on the complexity of the analysis. *dnsfastquery* can be used to speed up the process and save the raw DNS response for later analysis.

## Features and Properties

* *dnsfastquery* uses threads to parallelize DNS queries.
* Each thread creates a DNS-over-TCP keep-alive connection to a DNS resolver. This is supposed to save resources and reliably retrieve large DNS responses without truncation or fragmentation issues.
* *dnsfastquery* requires an external DNS resolver for name resolution. It's recommended to use BIND9 or Unbound (to benefit from caching and work around corner cases that happen all the time with DNS). Enable or disable DNSSEC validation to your liking. Please be considerate and do not run *dnsfastquery* against a DNS resolver used in a production environment.
* *dnsfastquery*'s priority is to retrieve reliable results rather than to achieve the highest possible throughput. Feel free to adapt THREAD_NUM and THREAD_SLEEP in `dnsfastquery.harvester` to optimize the performance.
* The responses are written to a single \*.dnsdata file in binary format. This approach follows a best practice for research efforts: decouple measurement and analysis. Save raw data during measurement and allow adaptation of the analysis script afterwards.

### .dnsdata File Format

The \*.dnsdata file can be parsed with `dnsfastquery.reader`. Function `read_file(filename)` gives you the responses in binary format and function `parse_file(filename)` as parsed `dns.message.Message` objects.

In case you prefer to implement your own binary parser, the file format follows:

```
dnsdatafile = *( result )
result = unixtime domainlen domain numresp *( response )
response = respsize respdata

Integers are in network byte order (big-endian).

Name        Data Type   Description
result      struct      Variable-length structure of metadata and responses

unixtime    uint32      Timestamp when responses have been retrieved
domainlen   uint8       Length of domain name string
domain      string      Variable-length UTF-8 encoded domain name
numresp     uint8       Number of responses following
response    struct      Variable-length response data structure

respsize    uint16      Size of DNS message
respdata    struct      Variable-length DNS message in wire format
```

## Usage

```
python3 -m dnsfastquery.harvester RESOLVER_ADDRESS domainlist.txt DNSTYPE...
python3 -m dnsfastquery.reader file.dnsdata
```

**Example**:
```
python3 -m dnsfastquery.harvester 127.0.0.1 example_domains.txt TXT
python3 example-read-dmarc.py example.dnsdata
```

## Installation

### Prerequisites

* [Python 3](https://www.python.org)
* [dnspython](https://www.dnspython.org)

### Download

* [dnsfastquery-0.1.tar.gz](dnsfastquery-0.1.tar.gz)
