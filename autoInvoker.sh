#!/usr/bin/env bash
# usage: $0 wolverine<machine_name> balanced_roi<experiment_name>
name=$1
experiment=$2

benchmarks=("bm_json_dumps" "bm_deltablue" "bm_pidigits" "bm_regex_v8")

for bench in "${benchmarks[@]}"
		do
		for i in 1 2 3
				do
						for rate in 10 20 30 40 50 60 70 80 90 100 110 120 130 140
								do
										./WorkloadInvoker -c configs/workload_configs.json -r $rate -b $bench -n "$name/$experiment/$bench/$i"_"$rate"
										sleep 10\*$rate
				done
		done
done
