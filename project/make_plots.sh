#!/bin/bash

cd server_implementation
# make -B run_release_simd CFLAGS+="-DSIMDBEST" # change this for SIMT
sleep 1
# python3 run_perf4.py
sleep 1
python3 run_plots4.py