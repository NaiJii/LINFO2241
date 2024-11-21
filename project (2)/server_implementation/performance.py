import subprocess
import re
import time
import os
import signal
import pandas as pd

def run_command(matsize, patterns_size, nb_patterns, duration, threads, connections, throughput):
    command = [
        "env",
        f"matsize={matsize}",
        f"patterns_size={patterns_size}",
        f"nb_patterns={nb_patterns}",
        "./../wrk2/wrk",
        "http://localhost:8888/",
        f"-d{duration}s",
        f"-t{threads}",
        f"-c{connections}",
        f"-R{throughput}",
        "-s",
        "wrk_scripts/simple_scenario.lua"
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
        output = result.stdout
        return parse_output(output)

    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)
        return None
    
def run_perf():
    command = [
        "perf",
        "stat",
        "-e",
        "cache-misses,cache-references",
        "./../wrk2/wrk",
        "http://localhost:8888/",
        "-d30s",
        "-t2",
        "-c100",
        "-R -1",
        "-s",
        "wrk_scripts/simple_scenario.lua"
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, shell=True)
        output = result.stdout
        return parse_output(output)

    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)
        return None

def parse_output(output):
    """
    Running 10s test @ http://localhost:8888/
  2 threads and 10 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     4.39s     2.54s    8.79s    57.53%
    Req/Sec       -nan      -nan   0.00      0.00%
  1243 requests in 10.01s, 195.43KB read
Requests/sec:    124.14
Transfer/sec:     19.52KB
    """
    parsed_values = {}
    latency_match = re.search(r'Latency\s+([\d.]+)(us|ms|s)\s+([\d.]+)(us|ms|s)\s+([\d.]+)(us|ms|s)', output)
    requests_match = re.search(r'(\d+)\s+requests', output)
    data_read_match = re.search(r'(\d+.\d+)([KM])B\s+read', output)
    requests_sec_match = re.search(r'Requests/sec:\s+([\d.]+)', output)
    transfer_sec_match = re.search(r'Transfer/sec:\s+([\d.]+)([KM])B', output)

    def convert_to_ms(value, unit):
        if unit == 'ms':
            return float(value)
        elif unit == 'us':
            return float(value) / 1000
        return float(value) * 1000
    
    def convert_to_bytes(value, unit):
        if unit == 'K':
            return float(value) * 1024
        elif unit == 'M':
            return float(value) * 1024 * 1024
        return float(value)

    if latency_match:
        # print(latency_match.groups())
        latency_avg = convert_to_ms(latency_match.group(1)[:-1], latency_match.group(2))
        latency_stdev = convert_to_ms(latency_match.group(3)[:-1], latency_match.group(4))
        latency_max = convert_to_ms(latency_match.group(5)[:-1], latency_match.group(6))
        parsed_values['latency_avg'] = latency_avg
        parsed_values['latency_stdev'] = latency_stdev
        parsed_values['latency_max'] = latency_max
    if requests_match:
        parsed_values['requests'] = int(requests_match.group(1))
    if data_read_match:
        parsed_values['data_read'] = convert_to_bytes(data_read_match.group(1), data_read_match.group(2))
    if transfer_sec_match:
        parsed_values['transfer_per_sec'] = convert_to_bytes(transfer_sec_match.group(1), transfer_sec_match.group(2))
    if requests_sec_match:
        parsed_values['requests_per_sec'] = float(requests_sec_match.group(1))
    return parsed_values

def performance_analysis(runs):
    all_results = []
    for run in runs:
        # matsize, patterns_size, nb_patterns, duration, threads, connections, throughput, flags
        matsize, patterns_size, nb_patterns, duration, threads, connections, throughput, flags = run
        try:
            result = run_command(*run)
            if result:
                all_results.append({
                    'matsize': matsize,
                    'patterns_size': patterns_size,
                    'nb_patterns': nb_patterns,
                    'duration': duration,
                    'threads': threads,
                    'connections': connections,
                    'throughput': throughput,
                    'flags': flags,
                    'requests': result.get('requests', 0),
                    'data_read': result.get('data_read', 0),
                    'requests_per_sec': result.get('requests_per_sec', 0),
                    'transfer_per_sec': result.get('transfer_per_sec', 0),
                })
                print(f"[{len(all_results) / len(runs) * 100:.2f}%] matsize={matsize}, patterns_size={patterns_size}, nb_patterns={nb_patterns}, d={duration}s, t={threads}, c={connections}, R={throughput}, f={flags}: {result}")
        except Exception as e:
            print(f"Run with matsize={matsize}, patterns_size={patterns_size}, nb_patterns={nb_patterns}, duration={duration}, threads={threads}, connections={connections}, throughput={throughput}, f={flags} failed with exception: {e}")
    return all_results

def main():
    # check if the file exists, if it does, ignore runs for which the results already exist
    try:
        results = pd.read_csv("performance_data123.csv")
    except FileNotFoundError:
        results = pd.DataFrame(columns=['matsize', 'patterns_size', 'nb_patterns', 'throughput', 'flags', 'requests', 'requests_per_sec', 'transfer_per_sec'])

    flags = ["-DCACHE_AWARE", "-DUNROLL", "-DBEST", "-DCACHE_AWARE -DUNROLL"]
    run_configs = []
    for flag in flags:
        # matsize, patterns_size, nb_patterns, duration, threads, connections, throughput, flags
        # matsize 64, 512
        run_configs.append((64, 4, 1, 30, 2, 100, -1, flag))
        run_configs.append((512, 4, 1, 30, 2, 100, -1, flag))
        # patterns_size 32, 128
        run_configs.append((64, 32, 16, 30, 2, 100, -1, flag))
        run_configs.append((64, 128, 16, 30, 2, 100, -1, flag))
        # nb_patterns 8, 128
        run_configs.append((64, 32, 8, 30, 2, 100, -1, flag))
        run_configs.append((64, 32, 128, 30, 2, 100, -1, flag))

    # matrix size ** 2 >= pattern size 
    run_configs = [run for run in run_configs if run[0] ** 2 >= run[1]]
    
    # thread count <= http connections
    # run_configs = [run for run in run_configs if run[4] <= run[5]]
    
    #existing_runs = results[['matsize', 'patterns_size', 'nb_patterns', 'duration', 'threads', 'connections', 'throughput']].apply(tuple, axis=1).tolist()

    #run_configs = [run for run in run_configs if run not in existing_runs]

    print(f"Total number of runs: {len(run_configs)}")
    
    performance_data = performance_analysis(run_configs)
    
    new_results = pd.DataFrame(performance_data)
    pd.concat([results, new_results], ignore_index=True).to_csv("performance_data.csv", index=False)
    
if __name__ == "__main__":
    main()
