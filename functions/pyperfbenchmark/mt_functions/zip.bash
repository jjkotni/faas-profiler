#!/bin/bash
if [ "$#" -ne 1 ]; then
		echo "Usage: $0 <benchmark_name>"
		exit 1
fi

# First argument to script is file name to be created
# eg. bm_unpack_sequence.zip
ZIP_NAME=$1".zip"

MAIN=__main__.py
DATA=data/

# Create chain of arguments
ARG=$MAIN
ARG+=" "$DATA

# This command creates the zip archive needed!
zip -r $ZIP_NAME $ARG
