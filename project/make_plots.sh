#!/bin/bash

cd server_implementation
make run_release
cd ..
cd ..

python3 run_perf.py
python3 run_plots.py