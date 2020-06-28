#!/bin/bash
for i in `seq 2 50`; do
    python3 memory_experiment_linz.py ndecomp $i
done

for i in `seq 2 50`; do
    python3 memory_experiment_linz.py decomp $i
done
