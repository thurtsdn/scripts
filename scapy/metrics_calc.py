#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function

import os
import sys
from scapy.all import *

class Metrics(object):
    def __init__(self):
        self.sum = 0
        self.square_sum = 0
        self.samples = 0
        self.min = sys.maxint
        self.max = 0

    def update(self, value):
        self.square_sum += value * value
        self.sum += value
        self.samples += 1

        if value > self.max:
            self.max = value
        if value < self.min:
            self.min = value

    def printm(self):
        average_ns = self.sum / float(self.samples)
        var_ns2 = self.square_sum / float(self.samples)
        print(type(self).__name__, ":")
        print("\tAverage:", average_ns, "us, Variance:", var_ns2, "us2")
        print("\tMax:", self.max, "us, Min:", self.min, "us")
        print("\tSamples:", self.samples)


class Latency(Metrics):
    def calc(self, send_time, recv_time):
        latency = recv_time - send_time
        self.update(latency)


class InterArrival(Metrics):
    def __init__(self):
        Metrics.__init__(self)
        self.last_recv = 0
        
    def calc(self, recv_time):
        if self.last_recv == 0:
            self.last_recv = recv_time
            return

        inter_arrival = recv_time - self.last_recv
        self.update(inter_arrival)
        
        self.last_recv = recv_time


class Jitter(Metrics):
    def __init__(self):
        Metrics.__init__(self)
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
    # get recv time, us
    recv_time = int(packet.time * 1000000)
    # get send time, us
    send_time = int(packet[Raw].load[8:16].encode('Hex'), 16) / 1000

    return send_time, recv_time


if __name__ == '__main__':
    pcap_dir = "/home/chenwh/Workspace/Data"
    pcap_path = os.path.join(pcap_dir, sys.argv[1]+".pcap")
    pcaps = rdpcap(pcap_path)

    latency = Latency()
    inter_arrival = InterArrival()
    jitter = Jitter()

    for packet in pcaps:
       if packet.haslayer('IP') and packet[IP].src == "10.0.0.1":
            send_time, recv_time = get_time(packet)
            # print("send time:", send_time, " recv time:", recv_time)
            latency.calc(send_time, recv_time)
            inter_arrival.calc(recv_time)
            jitter.calc(send_time, recv_time)

    latency.printm()
    inter_arrival.printm()
    jitter.printm()

