#!/usr/bin/env python3

# Dependencies:
import dns.rdatatype
import dns.message
import dnsfastquery.reader

import sys

def process_dmarc(dmarcdata):
    for unixtime, domain, responses in dmarcdata:
        if domain.startswith('_dmarc.'):
            domain = domain[7:]

        for rdata in responses:
            rmsg = dns.message.from_wire(rdata)
            for rrset in rmsg.answer:
                if rrset.rdtype != dns.rdatatype.TXT:
                    continue
                for rr in rrset:
                    txt = rr.to_text()
                    if 'v=dmarc' in txt.lower():
                        print('{}, {}'.format(domain, txt))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 example-read-dmarc.py file.dnsdata', file=sys.stderr)
        sys.exit(1)

    process_dmarc(dnsfastquery.reader.read_file(sys.argv[1]))
