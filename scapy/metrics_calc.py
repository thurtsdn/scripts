#!/usr/bin/env python
# coding=utf-8

import struct
from scapy.all import *

htonll = lambda a:struct.unpack('!Q', struct.pack('Q', a))[0]
ntohll = lambda a:struct.unpack('Q', struct.pack('!Q', a))[0]

class Metrics(object):
    def __init__(self):
        self.sum = 0
        self.square_sum = 0
        self.samples = 0
        self.min = 0
        self.max = 0

    def update(self, value):
        self.square_sum += value * value
        self.sum += value
        slef.samples += 1
        
        if value > self.max:
            self.max = value
        if value < self.min:
            self.min = value

    def print(self):
        average_ns = self.sum / float(self.samples)
        var_ns2 = self.square_sum / float(self.samples)
        print("\t\tAverage: %llu ns Variance %llu ns2\n", average_ns, var_ns2)
        print("\t\tMax: %llu ns Min:: %llu ns\n", self.max, self.min)
        print("\t\tSamples: %llu\n", self.samples)


class Latency(Metrics):
    def calc(self, send_time, recv_time):
        latency = recv_time - send_time
        self.update(latency)


class InterArrival(Metrics):
    def __init__(self):
        self.last_recv = 0
        
    def calc(self, recv_time):
        if self.last_recv == 0:
            return

        inter_arrival = recv_time - last_recv
        self.update(inter_arrival)
        
        self.last_recv = recv_time


class Jitter(Metrics):
    def __init__(self):
        self.last_latency = 0

    def calc(self, send_time, recv_time):
        latency = recv_time - send_time
        if self.last_latency == 0:
            self.last_latency = latency
            return

        jitter = abs(latency - self.last_latency)
        self.update(jitter)

        self.last_latency = latency


def get_time(packet):
    # get recv time
    recv_time = int(packet.time * 1000000000)
    # get send time
    stemp = int(packet[Raw].load[8:16].encode('Hex'), 16)
    send_time = ntohll(stemp)

    return send_time, recv_time


if __name__ == '__main__':
    pcap_path = "/home/chenwh/Workspace/Data/test.pcap"
    pcaps = rdpcap(pcap_path)

    latency = Latency()
    inter_arrival = InterArrival()
    jitter = Jitter()

    for packet in pcaps:
        if packet[IP].src == "10.0.0.1":
            send_time, recv_time = get_time(packet)
            latency.calc(send_time, recv_time)
            inter_arrival.calc(recv_time)
            jitter.calc(send_time, recv_time)

    latency.print()
    inter_arrival.print()
    jitter.print()

