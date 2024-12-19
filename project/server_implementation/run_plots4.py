import pandas as pd
import matplotlib.pyplot as plt

print("[INFO] Reading performance data")

results = pd.read_csv("performance_data4.csv")
grouped = results.groupby('flag')['requests_per_sec'].agg(['mean', 'var'])

fig, ax = plt.subplots()
grouped.plot(kind='bar', y='mean', yerr='var', ax=ax, capsize=4)
ax.set_xlabel('Flags')
ax.set_ylabel('Requests per Second (100 connections)')
# set custom names for the x-axis labels
ax.set_xticklabels(['Unoptimized(P2)', 'Best(P3)', 'Unrolling & C.A.(P3)', 'SIMD(P4)'])

# show x labels diagonally
plt.xticks(rotation=45)

plt.tight_layout()

plt.title("Mean and variance of throughput for each version")
plt.legend(['Mean', 'Variance'])
plt.savefig('throughput_variance.svg', format='svg')
plt.clf()
print("[INFO] Plot saved to throughput_variance.svg")