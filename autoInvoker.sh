#!/usr/bin/env bash
# Usage for expt.sh: ./expt.sh json_dumps<benchmark_name> chisel1<machine_name>
benchmark=$1
machine_name=$2

for i in 1 2 3 #run number
do
	for rate in 10 20 30 40 50 60 70 80 90 100 110 120 130 140 #invocation rate
	do
		./WorkloadInvoker -c $FAAS_ROOT/experiments/balanced_roi/config.json -r $rate -b $bench -n "$machine_name/$benchmark/$i"_"$rate"
		sleep 10\*$rate
	done
done