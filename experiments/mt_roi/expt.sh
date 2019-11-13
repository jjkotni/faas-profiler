#!/usr/bin/env bash
# Usage for expt.sh: ./expt.sh json_dumps<benchmark_name> chisel1<machine_name>
BENCHMARK=$1
MACHINE_NAME=$2
EXPERIMENT="mt_roi"
CONFIG_FILE="$FAAS_ROOT/experiments/$EXPERIMENT/config.json"

for RUN in 1 2 3 #run number
do
	for WORKERS in 2 4 6 8 10 12 #invocation rate
	do
		PARAM_FILE="$FAAS_ROOT/experiments/$EXPERIMENT/$WORKERS.json"
		./WorkloadInvoker -c $FAAS_ROOT/experiments/$EXPERIMENT/config.sh -c $CONFIG_FILE -r 10 -p $PARAM_FILE -b $BENCHMARK -n "$MACHINE_NAME/$EXPERIMENT/$BENCHMARK/$RUN"_"$WORKERS"
		sleep 60
	done
done