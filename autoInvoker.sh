#!/usr/bin/env bash

for i in 1 2 
    do
    for rate in 3 12 21 50 100 125; do
        ./WorkloadInvoker -c configs/workload_configs.json -r $rate -n cs_"$i"_"$rate"_90
        sleep 90
    done

<<Comment1
for i in 1 2 3 4 5 
    do
    for rate in 3 6 9 12 15 18 21 24 27 30 40 50 75 100 125; do
        ./WorkloadInvoker -c configs/workload_configs.json -r $rate -n cs_"$i"_"$rate"_20
        sleep 20
    done
for rate in 3 6 9 12 15 18 21 24 27 30 40 50 75 100 125; do
    ./WorkloadInvoker -c workload_configs.json -r $rate
    sleep 60

for rate in 3 6 9 12 15 18 21 24 27 30 40 50 75 100 125; do
    ./WorkloadInvoker -c workload_configs.json -r $rate
    sleep 120
Comment1
done
