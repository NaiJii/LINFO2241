import os
import signal
import subprocess
import time
import pandas as pd
import re
import csv

duration = 30

def generate_wrk_config():  
    global duration
    run_configs = []
    # matsize, patterns_size, nb_patterns, duration, threads, connections, throughput
    # matsize 64, 512
    run_configs.append((64, 4, 1, duration, 1, 100, -1))
    run_configs.append((512, 4, 1, duration, 1, 100, -1))
    # patterns_size 32, 128
    run_configs.append((64, 32, 16, duration, 1, 100, -1))
    run_configs.append((64, 128, 16, duration, 1, 100, -1))
    # nb_patterns 8, 128
    run_configs.append((64, 32, 8, duration, 1, 100, -1))
    run_configs.append((64, 32, 128, duration, 1, 100, -1))

    print(f"[INFO] Generated {len(run_configs)} run configurations.")

    cmds = []
    for run in run_configs:
        matsize, patterns_size, nb_patterns, duration, threads, connections, throughput = run
        cmd = [
            "env",
            f"matsize={matsize}",
            f"patterns_size={patterns_size}",
            f"nb_patterns={nb_patterns}",
            "../../wrk2/wrk",
            "http://localhost:8888/",
            f"-R {throughput}",
            f"-d{duration}s",
            f"-c{connections}",
            f"-t{threads}",
            "-s",
            "../wrk_scripts/simple_scenario.lua"
        ]
        cmds.append(cmd)
    return cmds

def generate_make_config():
    flags = ["", "-DUNROLL", "-DCACHE_AWARE", "-DBEST", "-DCACHE_AWARE -DUNROLL"]
    cmds = []
    for flag in flags:
        cmds.append(f"perf stat --timeout 30010 -o output.txt -e cache-misses,cache-references make -B run_release CFLAGS+='{flag}'")

    # try for different worker counts
    #for i in range(2, 11): 
    #    cmds.append(f"perf stat --timeout 30010 -o output.txt -e cache-misses,cache-references make -B run_release CFLAGS+=-DBEST NB_WORKER={i}")

    return cmds

def generate_make_worker_config():
    cmds = []
    for i in range(1, 11): 
        cmds.append(f"perf stat --timeout 30010 -o output.txt -e cache-misses,cache-references make -B run_release CFLAGS+=-DBEST NB_WORKER={i}")
    return cmds

def run_wrk(cmd):
    print(f"[INFO] Running wrk command: {cmd}")
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  

def run_make(cmd):
    print(f"[INFO] Running make command: {cmd}")
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True) 

def parse_wrk(output):
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
    print(f"[INFO] Running perf command: {cmd}")
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

def parse_perf(output):
    lines = output.split("\n")
    cache_misses = int(lines[0].split()[0])
    cache_references = int(lines[1].split()[0])
    return cache_misses, cache_references

def save_to_csv(results):
    f = "part3.csv"
    df = pd.DataFrame(results)
    df.to_csv(f, index=False)
    print("[INFO] Results saved to CSV:", f)

def generate_worker_csv():
    try:
        make_cfgs = generate_make_worker_config()
        wrk_cfg = [
            "env",
            f"matsize=512",
            f"patterns_size=8",
            f"nb_patterns=1",
            "../../wrk2/wrk",
            "http://localhost:8888/",
            f"-R -1",
            f"-d30s",
            f"-c100",
            f"-t1",
            "-s",
            "../wrk_scripts/simple_scenario.lua"
        ]

        results = []
        os.system("touch output.txt")

        for make_cmd in make_cfgs:
            run_make(make_cmd)  
            time.sleep(10)
            wrk = run_wrk(wrk_cfg)
            wrk.wait()
            wrk_output, _ = wrk.communicate()
            wrk_results = parse_wrk(wrk_output.decode())
            print(wrk.communicate())
            print(f"[INFO] WRK results: {wrk_results}")

            cache_misses = ""
            cache_references = ""

            with open("output.txt") as f:
                lines = f.readlines()
                temp = ""
                for line in lines:
                    temp += line
                
                cache_misses = temp.replace(" ", "").split('cache-misses')[0].split('\n')[-1].replace('.','')
                cache_references = temp.replace(" ", "").split('cache-references')[0].split('\n')[-1].replace('.','')
            f.close()

            results.append({
                'worker_count': make_cmd.split('NB_WORKER=')[1],
                'matsize': wrk_cfg[1].split('=')[1],
                'pattern_size': wrk_cfg[2].split('=')[1],
                'nb_patterns': wrk_cfg[3].split('=')[1],
                'transfers_per_sec': wrk_results['requests_per_sec'],
                'cache-misses': cache_misses,
                'cache-references': cache_references
            })

        print("[INFO] Server and tests completed.")

        print("Printing results:")
        print(results)

        data_file = open('performance_data_worker.csv', 'w')

        csv_writer = csv.writer(data_file)

        count = 0

        for result in results:
            if count == 0:
                csv_writer.writerow(result.keys())
                count += 1

            csv_writer.writerow(result.values())

        data_file.close()

    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
    finally:
        print("[INFO] Cleanup complete.")



def main():
    generate_worker_csv()
    return


    try:
        make_cfgs = generate_make_config()
        wrk_cfgs = generate_wrk_config()

        # Run WRK tests for each make configuration and save results into a csv. Parse both the make and wrk output to get the throughput.
        # Attach perf to the server process for each make configuration and save the perf output to a file.
        # for cache misses and cache references, use the following command: perf stat -e cache-misses,cache-references -o perf_output.txt -p <pid>
        results = []
        os.system("touch output.txt")
        for make_cmd in make_cfgs:
            for wrk_cmd in wrk_cfgs:
                run_make(make_cmd)  
                time.sleep(10)
                wrk = run_wrk(wrk_cmd)
                wrk.wait()
                wrk_output, _ = wrk.communicate()
                wrk_results = parse_wrk(wrk_output.decode())
                print(wrk.communicate())
                print(f"[INFO] WRK results: {wrk_results}")
                cache_misses = ""
                cache_references = ""
                time_elapsed = ""
                with open("output.txt") as f:
                    lines = f.readlines()
                    temp = ""
                    for line in lines:
                        temp += line
                    
                    cache_misses = temp.replace(" ", "").split('cache-misses')[0].split('\n')[-1].replace('.','')
                    cache_references = temp.replace(" ", "").split('cache-references')[0].split('\n')[-1].replace('.','')
                    time_elapsed = temp.replace(" ", "").split('secondstimeelapsed')[0].split('\n')[-1].replace('.','')
                #cache_misses, cache_references = parse_perf(perf_process.get_output())
                parsed_make_cmd = make_cmd.split('CFLAGS+=')[1][2:-1]
                results.append({
                    'make_cmd': parsed_make_cmd,
                    'matsize': wrk_cmd[1].split('=')[1],
                    'pattern_size': wrk_cmd[2].split('=')[1],
                    'nb_patterns': wrk_cmd[3].split('=')[1],
                    'transfers_per_sec': wrk_results['requests_per_sec'],
                    'cache-misses': cache_misses,
                    'cache-references': cache_references,
                    'time elapsed': time_elapsed
                })

        print("[INFO] Server and tests completed.")

            # Parse the perf output
            #with open("perf_output.txt") as f:
            #    lines = f.readlines()
            #    cache_misses = int(lines[0].split()[0])
            #    cache_references = int(lines[1].split()[0])
            #    print(f"[INFO] Cache misses: {cache_misses}, cache references: {cache_references}")

        print("Printing results:")
        print(results)

        data_file = open('performance_data.csv', 'w')
        
        csv_writer = csv.writer(data_file)
        
        count = 0
        
        for result in results:
            if count == 0:
                csv_writer.writerow(result.keys())
                count += 1
        
            csv_writer.writerow(result.values())
        
        data_file.close()

    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
    finally:
        print("[INFO] Cleanup complete.")

if __name__ == "__main__":
    main()