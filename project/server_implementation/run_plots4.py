import pandas as pd
import matplotlib.pyplot as plt

results = pd.read_csv("performance_data4.csv")
grouped = results.groupby('flags')['requests_per_sec'].agg(['mean', 'var'])

fig, ax = plt.subplots()
grouped.plot(kind='bar', y='mean', yerr='var', ax=ax, capsize=4)
ax.set_xlabel('Flags')
ax.set_ylabel('Requests per Second')
plt.title("Mean and Variance of Throughput for Each Version")
plt.savefig('throughput_variance.svg', format='svg')
plt.clf()