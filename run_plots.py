import pandas as pd
import matplotlib.pyplot as plt

results = pd.read_csv("./performance_data.csv")

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