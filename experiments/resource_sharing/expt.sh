#!/usr/bin/env bash
# Usage for expt.sh: ./expt.sh json_dumps<benchmark_name> chisel1<machine_name>
BENCHMARK=$1
MACHINE_NAME=$2

for RUN in 1  #run number
do
	for RATE in 100 #invocation rate
	do
		./WorkloadInvoker -c $FAAS_ROOT/experiments/resource_sharing/config.json -r $RATE -n "$MACHINE_NAME/resource_sharing/$BENCHMARK/$RUN"_"$RATE"
		#sleep $((10*$RATE))
	done
done
