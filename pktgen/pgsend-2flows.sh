#!/bin/bash

#modprobe pktgen

if [[ `lsmod | grep pktgen` == "" ]]; then
    modprobe pktgen
fi

function pgset() {
    local result

    echo $1 > $PGDEV

    result=`cat $PGDEV | fgrep "Result: OK:"`
    if [ "$result" = "" ]; then
         cat $PGDEV | fgrep Result:
    fi
}

function pg() {
    echo inject > $PGDEV
    cat $PGDEV
}

# Config Start Here -----------------------------------------------------------

# Number of CPUs. If you have more than 2.
CPUS=2
# Number of packets generated for each core.
PKTS=`echo "scale=0; 1000000/$CPUS" | bc`
# The rate of the stream.
RATEP=`echo "scale=0; 1000000/$CPUS" | bc`

# thread config
# Each CPU has own thread. 

for ((processor=0;processor<$CPUS;processor++))
#for processor in {0..1}
do
    PGDEV=/proc/net/pktgen/kpktgend_$processor
    echo "Removing all devices"
    pgset "rem_device_all"
done

for ((processor=0;processor<$CPUS;processor++))
#for processor in {0..1}
do
    PGDEV=/proc/net/pktgen/kpktgend_$processor
    echo "Adding h1-eth0"
    pgset "add_device h1-eth0@$processor" 
    echo "Setting max_before_softirq 1"
    #pgset "max_before_softirq 10000"
    PGDEV=/proc/net/pktgen/h1-eth0@$processor
    echo "Configuring $PGDEV"
    pgset "count 10000"
    pgset "flag QUEUE_MAP_CPU"
    #pgset "clone_skb 1000"
    pgset "pkt_size 64"
    pgset "delay 1000000000"
    pgset "src_min 10.0.0.1"
    pgset "src_max 10.0.0.1"
    pgset "dst 10.0.0.2"
    pgset "udp_src_min 8000"
    pgset "udp_src_max 8000"
    pgset "udp_dst_min 63000"
    pgset "udp_dst_max 63000"
    #pgset "flows 1024"
    #pgset "flowlen 4"
done

# Time to run
PGDEV=/proc/net/pktgen/pgctrl

echo "Running... ctrl^C to stop"
pgset "start" 
echo "Done"
