#!/usr/bin/env python3

# Bulk query sender for DNS queries
# Connects via TCP (with keepalive) to a recursive resolver
# Writes responses in binary format to disk

# Author: Matthaeus Wander <mail@wander.science>

# Dependencies:
import dns.message
import dns.rdatatype

import queue
import socket
import struct
import sys
import threading
import time

THREAD_NUM = 20
THREAD_SLEEP = 0.2 # each thread sleeps before processing the next domain
SOCKET_TIMEOUT = 60

class ResolveThread(threading.Thread):
    def __init__(self, resolver_address, domainlist, dnstypes, result_writer):
        threading.Thread.__init__(self)
        self.resolver_address = resolver_address
        self.domainlist = domainlist
        self.dnstypes = dnstypes
        self.result_writer = result_writer

        self.s = None

    def readfull(self, bytes):
        buflist = []
        l = 0
        while True:
            buf = self.s.recv(bytes - l)
            if len(buf) == 0:
                raise IOError('socket returned 0 bytes')
            buflist.append(buf)
            l += len(buf)

            if l == bytes:
                assert sum(map(lambda x: len(x), buflist)) == l
                return b''.join(buflist)

    def connect(self):
        if self.s is not None:
            try:
                self.s.close()
            except:
                pass

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.resolver_address, 53))
        self.s.settimeout(SOCKET_TIMEOUT)

    def send_query(self, domain, dnstype):
        qmsg = dns.message.make_query(domain, dnstype, use_edns=True, want_dnssec=True, payload=65535)

        qry = qmsg.to_wire()
        qrylen = struct.pack('>H', len(qry))

        self.s.send(qrylen + qry)

        buf = self.readfull(2)
        msglen, = struct.unpack('>H', buf)
        
        msg = self.readfull(msglen)
        #print('got resp', len(msg), 'bytes')

        tid, = struct.unpack('>H', msg[0:2])
        assert qmsg.id == tid

        return msg

    def process_network(self, domain):
        #print('Processing', domain, file=sys.stderr)
        responses = []
        
        for dnstype in self.dnstypes:
            rmsg = self.send_query(domain, dnstype)
            responses.append(rmsg)

        self.result_writer.put(int(time.time()), domain, responses)

    def run(self):
        print('Starting up', self, file=sys.stderr)
        self.connect()

        for domain in self.domainlist:
            while True:
                try:
                    self.process_network(domain)
                    time.sleep(THREAD_SLEEP)
                    break
                except socket.timeout:
                    print('timeout')
                except IOError as e:
                    print('socket error:', e)

                print('sleeping after error...')
                time.sleep(SOCKET_TIMEOUT)
                try:
                    self.connect()
                except:
                    print('connect failed')

class ResultWriter(threading.Thread):
    def __init__(self, filename):
        threading.Thread.__init__(self)
        self.filename = filename
        self.queue = queue.Queue()
        self.shut = False

    def put(self, unixtime, domain, responses):
        self.queue.put_nowait((unixtime, domain, responses))

    def run(self):
        print('Writing', self.filename, file=sys.stderr)
        with open(self.filename, 'wb') as fw:
            while True:
                try:
                    (unixtime, domain, responses) = self.queue.get(True, 3)
                    print('Writing for', domain, ', '.join(map(lambda r: '{} bytes'.format(len(r)), responses)))
                except queue.Empty:
                    if self.shut:
                        print('Wrote', fw.tell(), 'bytes to', self.filename, file=sys.stderr)
                        return
                    else:
                        continue

                fw.write(struct.pack('<I', unixtime))
                
                assert len(domain) <= 255
                wire_domain = domain.encode('utf-8')
                fw.write(struct.pack('B', len(wire_domain)))
                fw.write(wire_domain)
                
                assert len(responses) <= 255
                fw.write(struct.pack('B', len(responses)))

                for r in responses:
                    assert len(r) <= 65535
                    fw.write(struct.pack('<H', len(r)))
                    fw.write(r)

    def shutdown(self):
        self.shut = True

def mainloop(resolver_address, filename, dnstypes):
    """
    filename: filename of domainlist, which contains one domain per line
    dnstypes: list of DNS data types in text format
    """
    domains = []
    with open(filename, 'r') as f:
        for domain in f:
            domains.append(domain.strip())

    fname = '{}_fastquery.dnsdata'.format(int(time.time()))

    result_writer = ResultWriter(fname)
    result_writer.start()

    threads = []
    for i in range(THREAD_NUM):
        sliced = domains[i::THREAD_NUM]
        t = ResolveThread(resolver_address, sliced, dnstypes, result_writer)
        t.start()
        threads.append(t)
        time.sleep(float(1)/THREAD_NUM) # start interleaved

    # Wait until all threads have finished
    for t in threads:
        t.join()

    print('Shutting down...')
    result_writer.shutdown()
    result_writer.join()

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python3 -m dnsfastquery.harvester resolver domainlist.txt DNSTYPE...', file=sys.stderr)
        print('Example: python3 -m dnsfastquery.harvester 127.0.0.1 example_domains.txt TXT')
        sys.exit(1)
    else:
        mainloop(sys.argv[1], sys.argv[2], sys.argv[3:])
