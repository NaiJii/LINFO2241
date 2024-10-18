import subprocess
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_command(matsize, patterns_size, nb_patterns, duration, threads, connections, throughput):
    command = [
        "env",
        f"matsize={matsize}",
        f"patterns_size={patterns_size}",
        f"nb_patterns={nb_patterns}",
        "./wrk2/wrk",
        "http://localhost:8888/",
        f"-d{duration}s",
        f"-t{threads}",
        f"-c{connections}",
        f"-R{throughput}",
        "-s",
        "project/wrk_scripts/simple_scenario.lua"
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

    def convert_to_seconds(value, unit):
        if unit == 'ms':
            return float(value) / 1000
        elif unit == 'us':
            return float(value) / 1000000
        return float(value)

    if latency_match:
        print(latency_match.groups())
        latency_avg = convert_to_seconds(latency_match.group(1)[:-1], latency_match.group(2))
        latency_stdev = convert_to_seconds(latency_match.group(3)[:-1], latency_match.group(4))
        latency_max = convert_to_seconds(latency_match.group(5)[:-1], latency_match.group(6))
        parsed_values['latency_avg'] = latency_avg
        parsed_values['latency_stdev'] = latency_stdev
        parsed_values['latency_max'] = latency_max
    if requests_match:
        parsed_values['requests'] = int(requests_match.group(1))
    if data_read_match:
        data_read = float(data_read_match.group(1))
        if data_read_match.group(2) == 'K':
            data_read *= 1024
        elif data_read_match.group(2) == 'M':
            data_read *= 1024 * 1024
        parsed_values['data_read'] = data_read
    if transfer_sec_match:
        transfer_sec = float(transfer_sec_match.group(1))
        if transfer_sec_match.group(2) == 'K':
            transfer_sec *= 1024
        elif transfer_sec_match.group(2) == 'M':
            transfer_sec *= 1024 * 1024
        parsed_values['transfer_per_sec'] = transfer_sec
    if requests_sec_match:
        parsed_values['requests_per_sec'] = float(requests_sec_match.group(1))
    return parsed_values

def performance_analysis(runs, max_workers):
    all_results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_run = {executor.submit(run_command, *run): run for run in runs}

        for future in as_completed(future_to_run):
            run = future_to_run[future]
            matsize, patterns_size, nb_patterns, duration, threads, connections, throughput = run
            try:
                result = future.result()
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
                    print(f"[{len(all_results) / len(runs) * 100:.2f}% Result for run with matsize={matsize}, patterns_size={patterns_size}, nb_patterns={nb_patterns}, duration={duration}, threads={threads}, connections={connections}, throughput={throughput}: {result}")
                    # print(f"Results: {result} [{len(all_results) / len(runs) * 100:.2f}% complete]")
            except Exception as e:
                print(f"Run with matsize={matsize}, patterns_size={patterns_size}, nb_patterns={nb_patterns}, duration={duration}, threads={threads}, connections={connections}, throughput={throughput} failed with exception: {e}")

    return all_results

def main():
    matsize = [8]
    pattern_size = [2, 4]
    pattern_count = [1, 2] 
    benchmark_duration = [10]
    thread_count = [2]
    http_connections = [8]
    throughput = [1000, 2000]
    
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
    
    # thread count <= http connections16
    run_configs = [run for run in run_configs if run[4] <= run[5]]
    
    print(f"Total number of runs: {len(run_configs)}")
    
    max_workers = 4  # Set the maximum number of concurrent threads
    performance_data = performance_analysis(run_configs, max_workers)

    # save performance data to a csv file
    with open('performance_data.csv', 'w') as f:
        f.write('matsize,patterns_size,nb_patterns,duration,threads,connections,throughput,latency_avg,latency_stdev,latency_max,requests,data_read,requests_per_sec,transfer_per_sec\n')
        for data in performance_data:
            print(data)
            f.write(f"{data['matsize']},{data['patterns_size']},{data['nb_patterns']},{data['duration']},{data['threads']},{data['connections']},{data['throughput']},{data['latency_avg']},{data['latency_stdev']},{data['latency_max']},{data['requests']},{data['data_read']},{data['requests_per_sec']},{data['transfer_per_sec']}\n")

if __name__ == "__main__":
    main()
