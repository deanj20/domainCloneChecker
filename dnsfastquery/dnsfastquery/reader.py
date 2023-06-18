#!/usr/bin/env python3

# Parse .dnsdata files created by dnsfastquery.harvester

# Author: Matthaeus Wander <mail@wander.science>

# Dependencies:
import dns.message

import struct
import sys

def read_file(filename):
    """ file format:
    uint32  unixtime
    uint8   length of domain name string
    string  utf-8 encoded domain name
    uint8   number of response messages
    variable number of response messages follows, each with format:
    uint16  size of response message
    struct  DNS response in wire format
    """
    with open(filename, 'rb') as f:
        domain_count = 0
        while True:
            domain_count += 1

            buf = f.read(5)
            if len(buf) == 0:
                break
            unixtime, dlen = struct.unpack('<IB', buf)

            buf = f.read(dlen)
            domain = buf.decode('utf-8')

            buf = f.read(1)
            response_count, = struct.unpack('B', buf)

            responses = []
            for _ in range(response_count):
                buf = f.read(2)
                msglen, = struct.unpack('<H', buf)

                msg = f.read(msglen)
                responses.append(msg)

            yield unixtime, domain, responses

def parse_file(filename):
    for unixtime, domain, responses in read_file(filename):
        # convert list of raw bytes objects to list of parsed dns.message.Message objects
        messages = [ dns.message.from_wire(rdata) for rdata in responses ]
        yield unixtime, domain, messages


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 -m dnsfastquery.reader file.dnsdata', file=sys.stderr)
        sys.exit(1)
    
    for unixtime, domain, responses in parse_file(sys.argv[1]):
        print('###', unixtime, domain, 'has', len(responses), 'responses')

        for rmsg in responses:
            print('# ANSWER SECTION:')
            for a in rmsg.answer:
                print(a)

            print()

    parse_file(sys.argv[1])