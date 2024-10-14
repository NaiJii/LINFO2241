import subprocess
import re

def run_command(matsize, patterns_size, nb_patterns):
    command = [
        "env",
        f"matsize={matsize}",
        f"patterns_size={patterns_size}",
        f"nb_patterns={nb_patterns}",
        "./wrk2/wrk",
        "http://localhost:8888/",
        "-R1024",
        "-s",
        "project/wrk_scripts/simple_scenario.lua"
    ]

    try:
        # Execute the command and capture the output
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout

        # Parse the output
        parsed_data = parse_output(output)
        return parsed_data

    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)
        return None

def parse_output(output):
    # Initialize a dictionary to hold parsed values
    parsed_values = {}

    # Use regular expressions to extract data
    req_sec_match = re.search(r'Requests/sec:\s+([\d.]+)', output)
    transfer_sec_match = re.search(r'Transfer/sec:\s+([\d.]+)', output)

    if req_sec_match:
        parsed_values['requests_per_sec'] = float(req_sec_match.group(1))
    if transfer_sec_match:
        parsed_values['transfer_per_sec'] = float(transfer_sec_match.group(1))

    # Return the parsed values
    return parsed_values

# Example usage
matsize = 1
patterns_size = 1
nb_patterns = 2
result = run_command(matsize, patterns_size, nb_patterns)

if result:
    print("Parsed Results:", result)
