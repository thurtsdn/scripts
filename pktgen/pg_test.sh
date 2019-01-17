#!/bin/bash

if [[ `lsmod | grep pktgen` == "" ]]; then
    modprobe pktgen
fi

if [[ $1 == "" ]]; then
    pktsize=128
else
    pktsize=$1
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

echo "Adding devices to run".

PGDEV=/proc/net/pktgen/kpktgend_0

pgset "rem_device_all"
pgset "add_device h1-eth0"
pgset "max_before_softirq 1"

echo "Configuring devices"

PGDEV=/proc/net/pktgen/h1-eth0

pgset "clone_skb 1000"
pgset "pkt_size $pktsize"
pgset "src_min 10.0.0.1"
pgset "src_max 10.0.0.1"
pgset "dst 10.0.0.2"
pgset "count 0"

# Run

PGDEV=/proc/net/pktgen/pgctrl
echo "pktsize:$pktsize"
echo "Running... Ctrl^C to stop"

pgset "start"

echo "Done"
