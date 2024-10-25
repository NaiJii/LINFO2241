import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

plt.tight_layout()

results = pd.read_csv("performance_data.csv")
temp_results = pd.read_csv("performance_data_temp2.csv")

result_count = len(results)
print(f"Total number of results: {result_count}")

# filter out tests with requests == 0
results = results[results['requests'] > 0]
temp_results = temp_results[temp_results['requests'] > 0]
print(f"Number of results after filtering out tests with 0 requests: {len(results)}")

# get data for specific case(s) to avoid clutter, 
# e,g, get data for 1000 connections, 1 thread
def get_data(*args):
    data = results
    for arg in args:
        data = data[data[arg[0]] == arg[1]]
    return data

def get_temp_data(*args):
    data = temp_results
    for arg in args:
        data = data[data[arg[0]] == arg[1]]
    return data

def list_fix(x, isSorted = False, factor = 1):
    temp_list = list(x)
    temp_list = [i*factor for i in temp_list]
    if isSorted:
        temp_list.sort()
    return temp_list

# set all parameters to get data for a specific case
# e.g. get data for 1 thread, 20s duration, 1000 throughput, 10000 connections
t1_d20_tp1K_c10K = get_data(('threads', 1), ('duration', 20), ('throughput', 1000), ('connections', 10000))
t1_d20_tp1K_c10K = get_data(('threads', 1), ('duration', 10), ('throughput', 2000), ('connections', 1000))

# 10,1,4200,1000
temp_t1_d10_tp1K_c4200 = get_temp_data(('threads', 1), ('duration', 10), ('throughput', 1000), ('connections', 4200))
print("Number of results for 1 thread, 10s duration, 1000 throughput, 4200 connections: ", len(temp_t1_d10_tp1K_c4200))

matrix_sizes = temp_t1_d10_tp1K_c4200['matsize'].unique()
print("Matrix sizes: ", matrix_sizes)

if False:
    a = list_fix(t1_d20_tp1K_c10K['matsize'], isSorted=True)
    b = list_fix(t1_d20_tp1K_c10K['latency_avg'], factor=0.001)
    c = list_fix(t1_d20_tp1K_c10K['latency_stdev'], factor=0.001)

    fig, ax = plt.subplots()
    ax.errorbar(a, b, yerr=c, label='Latency (seconds)')
    ax.set_xscale('log', base=2)
    plt.legend()
    plt.xlabel('Matrix size')
    plt.ylabel('Average latency (seconds)')
    plt.title('Average latency by matrix size')
    plt.savefig('hejsan', format='svg')
    plt.show()
    plt.clf()

# remove the "throughput" column from the correlation matrix
temp = results.drop(columns=['throughput'])
plt.matshow(temp.corr())
plt.xticks(range(len(temp.columns)), temp.columns, rotation='vertical')
plt.yticks(range(len(temp.columns)), temp.columns)
plt.colorbar()
plt.title('Correlation matrix')
plt.savefig('results/correlation.svg', bbox_inches='tight', format='svg')

plt.scatter(results['latency_avg'], results['throughput'])
plt.title("Throughput vs. Latency Avg")
plt.xlabel("Average Latency (ms)")
plt.ylabel("Throughput (req/sec)")
plt.savefig('results/latency_avg_vs_throughput.svg', format='svg')
plt.clf()

avg_latency = results.groupby('patterns_size')['latency_avg'].mean()
avg_latency.plot(kind='bar')
plt.title("Average Latency by Pattern Size")
plt.xlabel("Pattern Size")
plt.ylabel("Average Latency (ms)")
plt.savefig('results/latency_by_pattern_size.svg', format='svg')
plt.clf()

requests_per_sec = results.groupby('connections')['requests_per_sec'].mean()
requests_per_sec.plot(kind='bar')
plt.title("Requests per Second by Connections")
plt.xlabel("Number of Connections")
plt.ylabel("Requests per Second")
plt.savefig('results/requests_per_sec_by_connections.svg', format='svg')
plt.clf()

plt.boxplot([results[results['nb_patterns'] == n]['latency_avg'] for n in results['nb_patterns'].unique()], labels=results['nb_patterns'].unique())
plt.title("Latency Distribution by Number of Patterns")
plt.xlabel("Number of Patterns")
plt.ylabel("Latency (ms)")
plt.savefig('results/latency_by_nb_patterns.svg', format='svg')
plt.clf()

avg_latency_by_matrix = results.groupby('matsize')['latency_avg'].mean()
avg_latency_by_matrix.plot(kind='bar')
plt.title("Average Latency by Matrix Size")
plt.xlabel("Matrix Size")
plt.ylabel("Average Latency (ms)")
plt.savefig('results/latency_by_matrix_size.svg', format='svg')
plt.clf()

avg_latency_by_pattern = results.groupby('patterns_size')['latency_avg'].mean()
avg_latency_by_pattern.plot(kind='bar')
plt.title("Average Latency by Pattern Size")
plt.xlabel("Pattern Size")
plt.ylabel("Average Latency (ms)")
plt.savefig('results/latency_by_pattern_size.svg', format='svg')
plt.clf()

avg_latency_by_nb_patterns = results.groupby('nb_patterns')['latency_avg'].mean()
avg_latency_by_nb_patterns.plot(kind='bar')
plt.title("Average Latency by Number of Patterns")
plt.xlabel("Number of Patterns")
plt.ylabel("Average Latency (ms)")
plt.savefig('results/latency_by_nb_patterns.svg', format='svg')
plt.clf()

avg_latency_by_threads = results.groupby('threads')['latency_avg'].mean()
avg_latency_by_threads.plot(kind='bar')
plt.title("Average Latency by Number of Threads")
plt.xlabel("Number of Threads")
plt.ylabel("Average Latency (ms)")
plt.savefig('results/latency_by_threads.svg', format='svg')
plt.clf()

avg_latency_by_connections = results.groupby('connections')['latency_avg'].mean()
avg_latency_by_connections.plot(kind='bar')
plt.title("Average Latency by Connections")
plt.xlabel("Number of Connections")
plt.ylabel("Average Latency (ms)")
plt.savefig('results/latency_by_connections.svg', format='svg')
plt.clf()

data_read_by_connection_count = results.groupby('connections')['data_read'].mean()
data_read_by_connection_count.plot()
plt.title("Data Read by Connection Count")
plt.xlabel("Number of Connections")
plt.ylabel("Data Read (bytes)")
plt.savefig('results/data_read_by_connection_count.svg', format='svg')
plt.clf()

data_read_by_matrix_size = results.groupby('matsize')['data_read'].mean()
data_read_by_matrix_size.plot()
plt.title("Data Read by Matrix Size")
plt.xlabel("Matrix Size")
plt.ylabel("Data Read (bytes)")
plt.savefig('results/data_read_by_matrix_size.svg', format='svg')
plt.clf()

### keep in mind we probably don't want to get ALL data whenever drawing the graphs,
### e.g. get data from specific case like 1000 connections, 1 thread to avoid clutter

## 1. throughput versus number of threads 
## we should see an increase in throughput as we increase the number of threads
## barplot, x = number of threads, y = throughput

## 2. average latency versus number of connections 
## barplot, x = number of connections

## show average latency for each throughput/threads
## barplot 

## 3. average latency versus matrix size/number of patterns/pattern size
## barplot, x = matrix size, y = average latency

if True:  
    ax = plt.figure().add_subplot(projection='3d')
    sc = ax.scatter(temp_t1_d10_tp1K_c4200['matsize'], temp_t1_d10_tp1K_c4200['nb_patterns'], temp_t1_d10_tp1K_c4200['patterns_size'], c=temp_t1_d10_tp1K_c4200['latency_avg'], cmap='viridis')

    ax.set_xlabel('Matrix Size')
    
    # exponential scale
    ax.set_xscale('log', base=0.5)
    
    ax.set_ylabel('Number of Patterns')
    #ax.set_yscale('log', base=2)
    ax.set_zlabel('Pattern Size')
    #ax.set_zscale('log')
    plt.title("Average Latency by Matrix Size, Number of Patterns, and Pattern Size")

    cbar = plt.colorbar(sc)
    cbar.set_label('Average Latency (ms)')

    plt.show()
    plt.savefig('results/latency_by_matrix_size_patterns_size.svg', format='svg')
    plt.clf()

