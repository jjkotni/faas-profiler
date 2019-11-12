FAAS_ROOT="/home/kjj/faas-profiler"
FAAS_ROOT="/home/kjj/faas-profiler"
if [[$1 -eq '']]; then
    echo "The length of the test should be provided as the first input argument."
    exit 1
fi 

TEST_DURATION=$1
PERF_OUT_FILE=$2
PERF_SAMPLING_INTERVAL=100  # ms (min = 10ms)
PQOS_SAMPLING_INTERVAL=1    # set sampling interval to Nx100ms

# Clear existing output files
sudo rm -rf *.out

# Run monitoring scripts
# << Uncomment any or all of the default scripts below to use them. >>
bash $FAAS_ROOT'/monitoring/Perf.sh' $TEST_DURATION $PERF_SAMPLING_INTERVAL $PERF_OUT_FILE &
#bash $FAAS_ROOT'/monitoring/PQOSMon.sh' $TEST_DURATION $PQOS_SAMPLING_INTERVAL &
# bash $FAAS_ROOT'/monitoring/Blktrace.sh' $TEST_DURATION &
