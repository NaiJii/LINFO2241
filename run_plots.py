import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



results = pd.read_csv("performance_data.csv")

# print how much data
print("Result count = ", len(results))

plt.matshow(results.corr())
plt.xticks(range(len(results.columns)), results.columns, rotation='vertical')
plt.yticks(range(len(results.columns)), results.columns)
plt.colorbar()
plt.savefig('results/correlation.png')

def plot(type, x_label, y_label, title, n, x_data, y_data):
    if type == 'bar':
        plt.bar(x_data, y_data)
    elif type == 'line':
        plt.plot(x_data, y_data)
    else:
        plt.boxplot(y_data)
        #plt.xticks() solve this later
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.savefig('results/plot' + str(n) +'.png')

    plt.clf()

plt.boxplot(results['transfer_per_sec'])
plt.xlabel('Matrix size')
plt.xticks([1], [8]) #change this later for the real data
plt.ylabel('Transfer per second')
plt.title('Something important')
plt.savefig('results/plot1.png')

plt.clf()

plot('bar', 'Pattern size', 'Transfer per second', 'Something important', 2, results['patterns_size'], results['transfer_per_sec'])

plot('bar', 'Number of patterns', 'Transfer per second', 'Something important', 3, results['nb_patterns'], results['transfer_per_sec'])

plt.boxplot(results['transfer_per_sec'])
plt.xlabel('Number of threads')
plt.ylabel('Transfer per second')
plt.xticks([1], [2]) #change this later for the real data
plt.title('Something important')
plt.savefig('results/plot4.png')

plt.clf()

plot('bar', 'Number of connections', 'Transfer per second', 'Something important', 5, results['connections'], results['transfer_per_sec'])

#format of the csv file
#matsize,patterns_size,nb_patterns,duration,threads,connections,throughput,latency_avg,latency_stdev,latency_max,requests,data_read,requests_per_sec,transfer_per_sec

plt.scatter(results['latency_avg'], results['throughput'])
plt.title("Throughput vs. Latency Avg")
plt.xlabel("Average Latency (ms)")
plt.ylabel("Throughput (req/sec)")
plt.show()
plt.savefig('results/latency_avg_vs_throughput.png')


avg_latency = results.groupby('patterns_size')['latency_avg'].mean()
avg_latency.plot(kind='bar')
plt.title("Average Latency by Pattern Size")
plt.xlabel("Pattern Size")
plt.ylabel("Average Latency (ms)")
plt.show()


requests_per_sec = results.groupby('connections')['requests_per_sec'].mean()
requests_per_sec.plot(kind='bar')
plt.title("Requests per Second by Connections")
plt.xlabel("Number of Connections")
plt.ylabel("Requests per Second")
plt.show()

plt.boxplot([results[results['nb_patterns'] == n]['latency_avg'] for n in results['nb_patterns'].unique()], labels=results['nb_patterns'].unique())
plt.title("Latency Distribution by Number of Patterns")
plt.xlabel("Number of Patterns")
plt.ylabel("Latency (ms)")
plt.show()




avg_latency_by_matrix = results.groupby('matsize')['latency_avg'].mean()
avg_latency_by_matrix.plot(kind='bar')
plt.title("Average Latency by Matrix Size")
plt.xlabel("Matrix Size")
plt.ylabel("Average Latency (ms)")
plt.show()


avg_latency_by_pattern = results.groupby('patterns_size')['latency_avg'].mean()
avg_latency_by_pattern.plot(kind='bar')
plt.title("Average Latency by Pattern Size")
plt.xlabel("Pattern Size")
plt.ylabel("Average Latency (ms)")
plt.show()

avg_latency_by_nb_patterns = results.groupby('nb_patterns')['latency_avg'].mean()
avg_latency_by_nb_patterns.plot(kind='bar')
plt.title("Average Latency by Number of Patterns")
plt.xlabel("Number of Patterns")
plt.ylabel("Average Latency (ms)")
plt.show()


avg_latency_by_threads = results.groupby('threads')['latency_avg'].mean()
avg_latency_by_threads.plot(kind='bar')
plt.title("Average Latency by Number of Threads")
plt.xlabel("Number of Threads")
plt.ylabel("Average Latency (ms)")
plt.show()


avg_latency_by_connections = results.groupby('connections')['latency_avg'].mean()
avg_latency_by_connections.plot(kind='bar')
plt.title("Average Latency by Connections")
plt.xlabel("Number of Connections")
plt.ylabel("Average Latency (ms)")
plt.show()


data_read_by_connection_count = results.groupby('connections')['data_read'].mean()
data_read_by_connection_count.plot()
plt.title("Data Read by Connection Count")
plt.xlabel("Number of Connections")
plt.ylabel("Data Read (bytes)")
plt.show()


data_read_by_matrix_size = results.groupby('matsize')['data_read'].mean()
data_read_by_matrix_size.plot()
plt.title("Data Read by Matrix Size")
plt.xlabel("Matrix Size")
plt.ylabel("Data Read (bytes)")
plt.show()


# show a graph showing the average latency by matrix size for different number of connections
# i want the number of connections on the x axis and the average latency on the y axis
# i want a single line for each matrix size
 
# for matrix_size in results['matsize'].unique():
#     data = results[results['matsize'] == matrix_size]
#     plt.plot(data['connections'], data['latency_avg'], label=matrix_size)
# plt.xlabel("Number of Connections")
# plt.ylabel("Average Latency (ms)")
# plt.title("Average Latency by Number of Connections")
# plt.legend()

# show a graph showing the average latency by matrix size for different number of threads
# i want the number of threads on the x axis and the average latency on the y axis
# i want a line for each matrix size

# for matrix_size in results['matsize'].unique():
#     data = results[results['matsize'] == matrix_size]
#     plt.plot(data['threads'], data['latency_avg'], label=matrix_size)
# plt.xlabel("Number of Threads")
# plt.ylabel("Average Latency (ms)")
# plt.title("Average Latency by Number of Threads")
# plt.legend()
# plt.show()




### grafer tycker jag skulle vara intressant att se

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
