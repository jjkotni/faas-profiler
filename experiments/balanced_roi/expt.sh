#!/usr/bin/env bash
# Usage for expt.sh: ./expt.sh json_dumps<benchmark_name> chisel1<machine_name>
BENCHMARK=$1
MACHINE_NAME=$2

for RUN in 1 2 #run number
do
	for RATE in 50 #invocation rate
	do
		./WorkloadInvoker -c $FAAS_ROOT/experiments/balanced_roi/config.json -r $RATE -b $BENCHMARK -n "$MACHINE_NAME/balanced_roi/$BENCHMARK/$RUN"_"$RATE"
		sleep $((10*$RATE))
	done
done
