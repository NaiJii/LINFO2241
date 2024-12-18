import subprocess
import re
import pandas as pd

def run_command(flags):
    command = [
        "env",
        "./../wrk2/wrk",
        "http://localhost:8888/",
        "-d30s",
        "-t1",
        "-c100",
        "-R1000",
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
    parsed_values = {}
    requests_sec_match = re.search(r'Requests/sec:\s+([\d.]+)', output)
    if requests_sec_match:
        parsed_values['requests_per_sec'] = float(requests_sec_match.group(1))
    return parsed_values

def performance_analysis(flags_list):
    all_results = []
    for flags in flags_list:
        result = run_command(flags)
        if result:
            all_results.append({
                'flags': flags,
                'requests_per_sec': result.get('requests_per_sec', 0)
            })
    return all_results

def main():
    flags_list = ["-DBEST", "-DSIMDBEST", "-DUNROLLING -DCACHE_AWARE", ""]
    performance_data = performance_analysis(flags_list)
    results = pd.DataFrame(performance_data)
    results.to_csv("performance_data4.csv", index=False)

if __name__ == "__main__":
    main()