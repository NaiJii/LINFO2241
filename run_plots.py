import pandas as pd
import matplotlib.pyplot as plt

#results = pd.read_csv("./results/results.csv")

#plt.plot(results['matsize'], results['transfer_per_sec'])
plt.boxplot([155944.96,311756.8,166922.24,333752.32,154920.96,164935.68,309800.96,329768.96])
plt.xlabel('Matrix size')
plt.xticks([1], [8]) #change this later for the real data
plt.ylabel('Transfer per second')
plt.title('Something important')
plt.savefig('results/plot1.png')

plt.clf()

#plt.bar(results['patterns_size], results['transfer_per_sec'])
plt.bar([2,2,2,2,4,4,4,4], [155944.96,311756.8,166922.24,333752.32,154920.96,164935.68,309800.96,329768.96])
plt.xlabel('Pattern size')
plt.ylabel('Transfer per second')
plt.title('Something important')
plt.savefig('results/plot2.png')

plt.clf()

#plt.bar(results['nb_patterns'], results['transfer_per_sec'])
plt.bar([1,1,2,2,1,2,1,2], [155944.96,311756.8,166922.24,333752.32,154920.96,164935.68,309800.96,329768.96])
plt.xlabel('Number of patterns')
plt.ylabel('Transfer per second')
plt.title('Something important')
plt.savefig('results/plot3.png')

plt.clf()

#plt.plot(results['threads'], results['transfer_per_sec'])
plt.boxplot([155944.96,311756.8,166922.24,333752.32,154920.96,164935.68,309800.96,329768.96])
plt.xlabel('Number of threads')
plt.ylabel('Transfer per second')
plt.xticks([1], [2]) #change this later for the real data
plt.title('Something important')
plt.savefig('results/plot4.png')

plt.clf()

#plt.plot(results['connections'], results['transfer_per_sec'])
plt.boxplot([155944.96,311756.8,166922.24,333752.32,154920.96,164935.68,309800.96,329768.96])
plt.xlabel('Number of connections')
plt.xticks([1], [8]) #change this later for the real data
plt.ylabel('Transfer per second')
plt.title('Something important')
plt.savefig('results/plot5.png')

plt.clf()

'''
matsize,patterns_size,nb_patterns,duration,threads,connections,throughput,latency_avg,latency_stdev,latency_max,requests,data_read,requests_per_sec,transfer_per_sec
8,2,1,10,2,8,1000,0,0,0,9996,1562378.24,999.65,155944.96
8,2,1,10,2,8,2000,0,0,0,19988,3114270.72,1998.51,311756.8
8,2,2,10,2,8,1000,0,0,0,9996,1667235.84,999.56,166922.24
8,2,2,10,2,8,2000,0,0,0,19989,3334471.68,1998.59,333752.32
8,4,1,10,2,8,1000,0,0,0,9996,1551892.48,999.54,154920.96
8,4,2,10,2,8,1000,0,0,0,9996,1646264.32,999.61,164935.68
8,4,1,10,2,8,2000,0,0,0,19988,3093299.2,1998.76,309800.96
8,4,2,10,2,8,2000,0,0,0,19988,3303014.4,1998.66,329768.96
'''