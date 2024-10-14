%info
Custom NPF Throughput Experiment for AI Detection System

%config
n_runs=5
var_names={MATSIZE:Matrix Size, PATTERNS_SIZE:Pattern Size, NB_PATTERNS:Number of Patterns, THROUGHPUT:Throughput}

%variables
MATSIZE={32,64,128,256}
PATTERNS_SIZE={32,64,128,256}
NB_PATTERNS={1,2,4,8}
TIME=2

%script@server
# Start the server
env matsize=64 patterns_size=64 nb_patterns=2 ./wrk2/wrk http://localhost:8888/ -R1024 -s project/wrk_scripts/simple_scenario.lua

%script@client 
for matsize in ${MATSIZE}; do
    for patterns_size in ${PATTERNS_SIZE}; do
        for nb in ${NB_PATTERNS}; do
            # Run the command with the specified parameters
            output=$(env matsize=$matsize patterns_size=$patterns_size nb_patterns=$nb ./wrk2/wrk http://localhost:8888/ -R1024 -s project/wrk_scripts/simple_scenario.lua 2>&1)

            # Log the output to a file
            echo "$output" | tee iperf.log

            # Parse the result to find the throughput
            result=$(cat iperf.log | grep -ioE "[0-9.]+ [kmg]bits" | tail -n 1)

            # Give the throughput to NPF through stdout
            echo "RESULT-THROUGHPUT MATSIZE=$matsize PATTERNS_SIZE=$patterns_size NB_PATTERNS=$nb THROUGHPUT=$result"
        done
    done
done

