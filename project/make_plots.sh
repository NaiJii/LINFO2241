#!/bin/bash

# Create a CSV file to store results
output_file="performance_results.csv"
echo "matsize,requests_per_sec,transfer_per_sec" > $output_file

# Run the Python script and capture its output
python3 ../run_tests.py | while IFS=',' read -r matsize req_sec trans_sec; do
    echo "$matsize,$req_sec,$trans_sec" >> $output_file
done

# Check if the performance results file exists
if [[ ! -f $output_file ]]; then
    echo "Error: $output_file not found."
    exit 1
fi

# Run the plotting script
python3 generate_plots.py

echo "Plots generated: requests_per_sec.png and transfer_per_sec.png"
