#!/bin/bash

cd server_implementation
make run_release
cd ..

python3 run_plots3.py