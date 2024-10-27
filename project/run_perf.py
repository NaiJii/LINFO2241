import subprocess
import re
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
        result = subprocess.run(command, capture_output=True, text=True, check=True)
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
        matsize, patterns_size, nb_patterns, duration, threads, connections, throughput = run
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
                    'latency_avg': result.get('latency_avg', 0),
                    'latency_stdev': result.get('latency_stdev', 0),
                    'latency_max': result.get('latency_max', 0),
                    'requests': result.get('requests', 0),
                    'data_read': result.get('data_read', 0),
                    'requests_per_sec': result.get('requests_per_sec', 0),
                    'transfer_per_sec': result.get('transfer_per_sec', 0),
                })
                print(f"[{len(all_results) / len(runs) * 100:.2f}%] matsize={matsize}, patterns_size={patterns_size}, nb_patterns={nb_patterns}, d={duration}s, t={threads}, c={connections}, R={throughput}: {result}")
                # print(f"Results: {result} [{len(all_results) / len(runs) * 100:.2f}% complete]")
        except Exception as e:
            print(f"Run with matsize={matsize}, patterns_size={patterns_size}, nb_patterns={nb_patterns}, duration={duration}, threads={threads}, connections={connections}, throughput={throughput} failed with exception: {e}")
    return all_results

def main():
    # check if the file exists, if it does, ignore runs for which the results already exist
    try:
        results = pd.read_csv("performance_data.csv")
    except FileNotFoundError:
        results = pd.DataFrame(columns=['matsize', 'patterns_size', 'nb_patterns', 'duration', 'threads', 'connections', 'throughput', 'latency_avg', 'latency_stdev', 'latency_max', 'requests', 'data_read', 'requests_per_sec', 'transfer_per_sec'])

    # change parameters here to append to performance data.
    matsize = [8]
    pattern_size = [8]  
    pattern_count = [1]
    benchmark_duration = [10]
    thread_count = [1]
    http_connections = [1000]
    throughput = [1000]
    
    run_configs = []
    for m in matsize:
        for p in pattern_size:
            for n in pattern_count:
                for d in benchmark_duration:
                    for t in thread_count:
                        for c in http_connections:
                            for tp in throughput:
                                run_configs.append((m, p, n, d, t, c, tp))
                                
    # matrix size ** 2 >= pattern size 
    run_configs = [run for run in run_configs if run[0] ** 2 >= run[1]]
    
    # thread count <= http connections
    run_configs = [run for run in run_configs if run[4] <= run[5]]
    
    existing_runs = results[['matsize', 'patterns_size', 'nb_patterns', 'duration', 'threads', 'connections', 'throughput']].apply(tuple, axis=1).tolist()

    run_configs = [run for run in run_configs if run not in existing_runs]

    print(f"Total number of runs: {len(run_configs)}")
    
    performance_data = performance_analysis(run_configs)
    
    new_results = pd.DataFrame(performance_data)
    pd.concat([results, new_results], ignore_index=True).to_csv("performance_data.csv", index=False)
    
if __name__ == "__main__":
    main()
