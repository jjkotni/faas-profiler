#This script should always be in the root folder of fass-profiler
#Usage: ./run_experiments.sh balanced_roi<expt-name> bm_json_dumps<bmk-name> csl-d4<machine-name>

EXPT=$1
BMK=$2 
MACHINE=$3
RUN_PLOT_ONLY=$4

#Set FAAS_ROOT
export FAAS_ROOT=$(pwd)

export WSK_CONFIG_FILE=~/openwhisk-devtools/docker-compose/.wskprops

if [ $RUN_PLOT_ONLY -ne 1 ]; then
    bash $FAAS_ROOT/functions/pyperfbenchmark/deploy.sh

    #Run expt init doing the following
    python3.6 expt_setup.py -e $EXPT -b $BMK -m $MACHINE

    #Run the expt
    bash $FAAS_ROOT/experiments/$EXPT/expt.sh $BMK $MACHINE
fi

#Run the plotter
python3.6 $FAAS_ROOT/experiments/$EXPT/plot.py -b $BMK -m $MACHINE
