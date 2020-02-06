#!/bin/bash
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <benchmark_name>"
    exit 1
fi

# Build benchmark names
BM=$1".py"
MT_BM="mt_"$BM
MP_BM="mp_"$BM

# Build stat and record output names
MT_STAT="mt_"$1"_stat.out"
MP_STAT="mp_"$1"_stat.out"
S_STAT="sub_"$1"_stat.out"
MT_RECORD="mt_"$1"_record.out"
MP_RECORD="mp_"$1"_record.out"
S_RECORD="sub_"$1"_record.out"

mkdir perf
#################################################
sudo perf stat -e cpu-cycles,L1-dcache-loads,L1-dcache-load-misses,L1-icache-load-misses,dTLB-load-misses,dTLB-loads,iTLB-load-misses,iTLB-loads,branch-misses,context-switches,cpu-migrations,page-faults python3.6 __main__.py 5 $BM 2> perf/$S_STAT

sudo perf record -e cycles:k python3.6 __main__.py 5 $BM
sudo perf report > perf/$S_RECORD
#################################################
sudo perf stat -e cpu-cycles,L1-dcache-loads,L1-dcache-load-misses,L1-icache-load-misses,dTLB-load-misses,dTLB-loads,iTLB-load-misses,iTLB-loads,branch-misses,context-switches,cpu-migrations,page-faults python3.6 $MT_BM 2> perf/$MT_STAT

sudo perf record -e cycles:k python3.6 $MT_BM
sudo perf report > perf/$MT_RECORD

#################################################
sudo perf stat -r 5 -e cpu-cycles,L1-dcache-loads,L1-dcache-load-misses,L1-icache-load-misses,dTLB-load-misses,dTLB-loads,iTLB-load-misses,iTLB-loads,branch-misses,context-switches,cpu-migrations,page-faults python3.6 $MP_BM 2> perf/$MP_STAT

sudo perf record -e cycles:k python3.6 $MP_BM
sudo perf report > perf/$MP_RECORD

################################################# Do Something post processing
