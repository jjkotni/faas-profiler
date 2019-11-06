#!/usr/bin/env bash

for i in 1 2 3 4 5  
    do
    for rate in 3 6 9 12 15 18 21 24 27 30 40 50 75 100 125; do
        ./WorkloadInvoker -c configs/workload_configs.json -r $rate -n cs_"$i"_"$rate"_20
        sleep 20
    done
done

for i in 1 2 3 4 5  
    do
    for rate in 3 6 9 12 15 18 21 24 27 30 40 50 75 100 125; do
        ./WorkloadInvoker -c configs/workload_configs.json -r $rate -n cs_"$i"_"$rate"_60
        sleep 60
    done

done

for i in 1 2 3 4 5  
    do
    for rate in 3 6 9 12 15 18 21 24 27 30 40 50 75 100 125; do
        ./WorkloadInvoker -c configs/workload_configs.json -r $rate -n cs_"$i"_"$rate"_120
        sleep 120
    done
done

for i in 1 2 3 4 5  
    do
    for rate in 3 6 9 12 15 18 21 24 27 30 40 50 75 100 125; do
        ./WorkloadInvoker -c configs/workload_configs.json -r $rate -n cs_"$i"_"$rate"_45
        sleep 45
    done
done
