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

def list_fix(x, isSorted = False, factor = 1):
    temp_list = list(x)
    temp_list = [i*factor for i in temp_list]
    if isSorted:
        temp_list.sort()
    return temp_list

# set all parameters to get data for a specific case
# e.g. get data for 1 thread, 20s duration, 1000 throughput, 10000 connections
t1_d20_tp1K_c10K = results[(results['threads'] == 1) & (results['duration'] == 20) & (results['throughput'] == 1000) & (results['connections'] == 10000)]
t1_d20_tp1K_c1K = results[(results['threads'] == 1) & (results['duration'] == 20) & (results['throughput'] == 1000) & (results['connections'] == 1000)]
t1_d20_tp1K_c100 = results[(results['threads'] == 1) & (results['duration'] == 20) & (results['throughput'] == 1000) & (results['connections'] == 100)]

# 10,1,4200,1000
t1_d10_tp1K_c4200 = temp_results[(temp_results['threads'] == 1) & (temp_results['duration'] == 10) & (temp_results['throughput'] == 1000) & (temp_results['connections'] == 4200)]

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
plt.savefig('measurements/correlation.svg', bbox_inches='tight', format='svg')

avg_latency = results.groupby('patterns_size')['latency_avg'].mean()
avg_latency.plot(kind='bar')
plt.title("Average Latency by Pattern Size")
plt.xlabel("Pattern Size")
plt.ylabel("Average Latency (ms)")
plt.savefig('measurements/latency_by_pattern_size.svg', format='svg')
plt.clf()

requests_per_sec = results.groupby('connections')['requests_per_sec'].mean()
requests_per_sec.plot(kind='bar')
plt.title("Requests per Second by Connections")
plt.xlabel("Number of Connections")
plt.ylabel("Requests per Second")
plt.savefig('measurements/requests_per_sec_by_connections.svg', format='svg')
plt.clf()

plt.boxplot([results[results['nb_patterns'] == n]['latency_avg'] for n in results['nb_patterns'].unique()], labels=results['nb_patterns'].unique())
plt.title("Latency Distribution by Number of Patterns")
plt.xlabel("Number of Patterns")
plt.ylabel("Latency (ms)")
plt.savefig('measurements/latency_by_nb_patterns.svg', format='svg')
plt.clf()

avg_latency_by_matrix = results.groupby('matsize')['latency_avg'].mean()
avg_latency_by_matrix.plot(kind='bar')
plt.title("Average Latency by Matrix Size")
plt.xlabel("Matrix Size")
plt.ylabel("Average Latency (ms)")
plt.savefig('measurements/latency_by_matrix_size.svg', format='svg')
plt.clf()

avg_latency_by_nb_patterns = results.groupby('nb_patterns')['latency_avg'].mean()
avg_latency_by_nb_patterns.plot(kind='bar')
plt.title("Average Latency by Number of Patterns")
plt.xlabel("Number of Patterns")
plt.ylabel("Average Latency (ms)")
plt.savefig('measurements/latency_by_nb_patterns.svg', format='svg')
plt.clf()

#avg_latency_by_threads = results.groupby('threads')['latency_avg'].mean()
#avg_latency_by_threads.plot(kind='bar')
#plt.title("Average Latency by Number of Threads")
#plt.xlabel("Number of Threads")
#plt.ylabel("Average Latency (ms)")
#plt.savefig('measurements/latency_by_threads.svg', format='svg')
#plt.clf()

r = results[(results['threads'] == 1) & (results['duration'] == 20) & (results['throughput'] == 1000)]
data_ = r.groupby('connections')['latency_avg'].mean()
#divide by 1000 to get seconds
data_ = data_ / 1000

data_.plot(kind='bar')
plt.title("Average Latency by connections")
plt.xlabel("Number of connections")
plt.ylabel("Average Latency (s)")
plt.savefig('measurements/latency_by_connections.svg', format='svg')
plt.clf()

#data_read_by_connection_count = results.groupby('connections')['data_read'].mean()
#data_read_by_connection_count.plot()
#plt.title("Data Read by Connection Count")
#plt.xlabel("Number of Connections")
#plt.ylabel("Data Read (bytes)")
#plt.savefig('measurements/data_read_by_connection_count.svg', format='svg')
#plt.clf()

# data_read_by_matrix_size = results.groupby('matsize')['data_read'].mean()
# data_read_by_matrix_size.plot()
# plt.title("Data Read by Matrix Size")
# plt.xlabel("Matrix Size")
# plt.ylabel("Data Read (bytes)")
# plt.savefig('measurements/data_read_by_matrix_size.svg', format='svg')
# plt.clf()

## 3. average latency versus matrix size/number of patterns/pattern size
if True:  
    x = list_fix(t1_d20_tp1K_c100['matsize'], isSorted=False)
    y = list_fix(t1_d20_tp1K_c100['patterns_size'], isSorted=False)
    z = list_fix(t1_d20_tp1K_c100['nb_patterns'], isSorted=False)
    c = list_fix(t1_d20_tp1K_c100['latency_avg'], factor=0.001)
    
    x = np.log2(x)
    y = np.log2(y)
    z = np.log2(z)
     
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    sc = ax.scatter(x, y, z, c=c, cmap='viridis', marker='o')

    ax.set_xlabel('Matrix Size')
    ax.set_ylabel('Pattern Size')
    ax.set_zlabel('Number of Patterns')
    plt.title("Average Latency for hyperparameters (logarithmic scale)")
    cbar = plt.colorbar(sc)
    cbar.set_label('Average Latency (s)')

    plt.show()
    plt.savefig('measurements/latency_by_matrix_size_patterns_size.svg', format='svg')
    plt.clf()

if False:
    # 4. average latency versus number of connections
    # line graph
    d = results[(results['matsize'] == 32) & (results['duration'] == 20) & (results['threads'] == 1) & (results['throughput'] == 1000)]
    print(len(d))
    a = list_fix(d['connections'], isSorted=True)
    b = list_fix(d['latency_avg'], factor=0.001)
    
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.plot(a, b, 'g-')
    ax.set_xlabel('Number of Connections')
    ax.set_ylabel('Average Latency (s)')
    plt.title("Average Latency by Number of Connections")
    plt.savefig('measurements/latency_by_connections.svg', format='svg')
    plt.show()
    plt.clf()
    
if False:
    # 5. matrix size vs. transfer per second
    d = results[(results['duration'] == 20) & (results['threads'] == 1) & (results['throughput'] == 1000) & (results['connections'] == 100) & (results['patterns_size'] == 32)]
    a = list_fix(d['matsize'], isSorted=True)
    b = list_fix(d['transfer_per_sec'], isSorted=False, factor=0.001)
    c = list_fix(d['requests_per_sec'], isSorted=False)
    
    # i want the x axis to be the matrix size   
    x = np.arange(len(a))
    
    
    fig, ax = plt.subplots()
    ax2 = ax.twinx()
    ax.plot(a, b, color='b', label='Transfer per Second')
    ax2.plot(a, c, 'g-', label='Requests per Second')
    ax.set_xlabel('Matrix Size')
    ax.set_ylabel('Transfer per Second (KB)', color='b')
    ax2.set_ylabel('Requests per Second', color='g')
    plt.title("Transfer per Second and Requests per Second by Matrix Size")
    plt.savefig('measurements/transfer_requests_by_matrix_size.svg', format='svg')
    plt.show()
    plt.clf()
    
if False:
    # t1_d20_tp1K_c100 = results[(results['threads'] == 1) & (results['duration'] == 20) & (results['throughput'] == 1000) & (results['connections'] == 100)]
    a = results[(results['duration'] == 20) & (results['matsize'] == 32) & (results['patterns_size'] == 32) & (results['nb_patterns'] == 8)]
    print(len(a))
    
    c = list_fix(a['connections'], isSorted=True)
    r = list_fix(a['requests_per_sec'], isSorted=False)
    t = list_fix(a['transfer_per_sec'], isSorted=False)
    
    fig = plt.figure()
    ax1 = fig.add_subplot()
    ax2 = ax1.twinx()
    
    ax1.plot(c, r, 'g-')
    ax2.plot(c, t, 'b-')
    
    ax1.set_xlabel('Number of Connections')
    ax1.set_ylabel('Requests per Second', color='g')
    ax2.set_ylabel('Transfer per Second', color='b')
    plt.title("Requests per Second and Transfer per Second by Number of Connections")
    plt.legend()
    
    plt.show()
    plt.savefig('measurements/requests_transfer_by_connections.svg', format='svg')
    plt.clf()
    results
if True:
    # latency distribution by matrix size 
    fig = plt.figure()
    ax = fig.add_subplot()
    
    x = t1_d20_tp1K_c100['matsize'].unique()
    y = [t1_d20_tp1K_c100[t1_d20_tp1K_c100['matsize'] == i]['latency_avg'] for i in x]
    # divide by 1000 to get seconds
    y = [list_fix(i, isSorted=False, factor=0.001) for i in y]
    # log scale
    y = [np.log10(i) for i in y]
    
    # one boxplot for each matrix size
    ax.boxplot(y, labels=x)
    ax.set_xlabel('Matrix Size')
    ax.set_ylabel('Average Latency (10^x s)')

    plt.title("Latency Distribution by Matrix Size (logrithmic scale)")
    plt.savefig('measurements/latency_distribution_by_matrix_size.svg', format='svg')
    plt.show()
    
    
    
# 