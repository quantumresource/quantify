#!/bin/bash

for ((i=0;i<8;i++)); do
    cpufreq-set -c $i --max $1MHz -r -g performance
done

cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
