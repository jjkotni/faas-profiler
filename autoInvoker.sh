#!/usr/bin/env bash

for i in 1 2 3  
    do
    for rate in 10 20 30 40 50 60 70 80 90 100 110; do
        ./WorkloadInvoker -c configs/workload_configs.json -r $rate -n "$1/$2/$3/$i"_"$rate"
        sleep 30
    done
done
