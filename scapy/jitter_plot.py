#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function

import os
import sys
from scapy.all import *
import matplotlib.pyplot as plt
import pylab as mpl

class Jitters(object):
    def __init__(self):
        self.jitters = []
        self.last_latency = 0
    
    def calc(self, send_time, recv_time):
        latency = recv_time - send_time
        if self.last_latency == 0:
            self.last_latency = latency
            return

        jitter = abs(latency - self.last_latency)
        self.jitters.append(jitter)

        self.last_latency = latency


def get_time(packet):
    # get recv time, us
    recv_time = int(packet.time * 1000000)
    # get send time, us
    send_time = int(packet[Raw].load[8:16].encode('Hex'), 16) / 1000

    return send_time, recv_time


if __name__ == '__main__':
    pcap_dir = "/home/chenwh/Workspace/data"
    rt_pcap_path = os.path.join(pcap_dir, sys.argv[1]+".pcap")
    nrt_pcap_path = os.path.join(pcap_dir, sys.argv[2]+".pcap")
    rt_pcaps = rdpcap(rt_pcap_path)
    nrt_pcaps = rdpcap(nrt_pcap_path)

    mpl.rcParams['font.sans-serif'] = ['SimHei']
    mpl.rcParams['font.family']='sans-serif'

    rt_jitters = Jitters()
    nrt_jitters = Jitters()

    for packet in rt_pcaps:
       if packet.haslayer('IP') and packet[IP].src == "10.0.0.1":
            send_time, recv_time = get_time(packet)
            rt_jitters.calc(send_time, recv_time)

    for packet in nrt_pcaps:
       if packet.haslayer('IP') and packet[IP].src == "10.0.0.1":
            send_time, recv_time = get_time(packet)
            nrt_jitters.calc(send_time, recv_time)

    x = range(0, 9752)
    plt.figure(1)
    plt.subplot(1, 2, 1)
    plt.plot(x, rt_jitters.jitters[:9752], color="r", linestyle="-", linewidth=0.5)
    plt.ylim(0, 180000)
    plt.xlabel(u"数据包个数")
    plt.ylabel(u"抖动值(us)")
    plt.title(u"实时性扩展转发抖动值变化")

    plt.subplot(1, 2, 2)
    plt.plot(x, nrt_jitters.jitters[:9752], linestyle="-", linewidth=0.5)
    plt.ylim(0, 180000)
    plt.xlabel(u"数据包个数")
    plt.ylabel(u"抖动值(us)")
    plt.title(u"一般路由转发抖动值变化")

    plt.show()

