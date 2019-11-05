#!/usr/bin/env bash

for rate in 3 6 9 12 15 18 21 24 27 30 40 50 75 100 125; do
    ./WorkloadInvoker -c workload_configs.json -r $rate
    sleep 20
done
