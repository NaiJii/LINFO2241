import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



import os
if not os.path.exists('measurements'):
    os.makedirs('measurements')

plt.tight_layout()

def format_number(num):
    if num >= 1e9:
        return f'{num/1e9:.1f}B'
    if num >= 1e6:
        return f'{num/1e6:.1f}M'
    elif num >= 1e3:
        return f'{num/1e3:.1f}K'
    else:
        return f'{num:.1f}'

results = pd.read_csv("performance_data.csv")
#make_cmd,matsize,pattern_size,nb_patterns,transfers_per_sec,cache-misses,cache-references,time elapsed
worker_results = pd.read_csv("performance_data_worker.csv")

for index, row in results.iterrows():
    if (index % 6) == 0:
        print('----------------------')
    print(round((float(row['cache-misses'].replace(",","")) / float(row['cache-references'].replace(",","")) * 100), 2))
    
def plot_case(name, title, n1, n2, pre_ledger, aft_ledger):
    case_y_pre = []
    case_y_aft = []
    for index, row in results.iterrows():
        if index % 6 == n1:
            case_y_pre.append(row['transfers_per_sec'])
        elif index % 6 == n2:
            case_y_aft.append(row['transfers_per_sec'])
    # Move the BEST flag to the last position
    case_y_pre = case_y_pre[:3] + [case_y_pre[4]] + [case_y_pre[3]]
    case_y_aft = case_y_aft[:3] + [case_y_aft[4]] + [case_y_aft[3]]
    barWidth = 0.25
    plt.figure(figsize =(12, 8))
    br1 = np.arange(len(case_y_pre)) 
    br2 = [x + barWidth for x in br1]  
    plt.bar(br1, case_y_pre, color ='black', width = barWidth, 
            edgecolor ='grey', label = pre_ledger) 
    plt.bar(br2, case_y_aft, color ='grey', width = barWidth, 
            edgecolor ='grey', label = aft_ledger) 
    plt.yscale("log")
    if len(set(case_y_pre + case_y_aft)) == 1:
        plt.ylim([min(case_y_pre + case_y_aft) * 0.9, max(case_y_pre + case_y_aft) * 1.1])
    plt.xlabel('Compile flags', fontweight ='bold', fontsize = 22) 
    plt.ylabel('Transfers per second', fontweight ='bold', fontsize = 22) 
    plt.xticks([r + (barWidth/2) for r in range(len(case_y_pre))], 
            ['NONE', 'UNROLL', 'CACHE AWARE', 'UNROLL & CACHE AWARE', 'BEST'], fontsize=16)
    plt.legend(fontsize = 16, loc='upper right')
    plt.title(title, fontweight = 'bold', fontsize = 30)
    plt.savefig('measurements/case_' + name + '.svg', format='svg')
    plt.close()

def plot_case_cache(name, title, n1, n2, n3, l1, l2, l3, stat, log=False):
    misses_1 = []
    misses_2 = []
    misses_3 = []

    for index, row in results.iterrows():
        if index % 6 == n1:
            misses_1.append(float(row[stat].replace(",", "")))
        elif index % 6 == n2:
            misses_2.append(float(row[stat].replace(",", "")))
        elif index % 6 == n3:
            misses_3.append(float(row[stat].replace(",", "")))
    
    misses_1 = misses_1[:3] + [misses_1[4]] + [misses_1[3]]
    misses_2 = misses_2[:3] + [misses_2[4]] + [misses_2[3]]
    misses_3 = misses_3[:3] + [misses_3[4]] + [misses_3[3]]
    barWidth = 0.25
    
    fig, ax1 = plt.subplots(figsize=(12, 8))
    br1 = np.arange(len(misses_1))
    ax1.bar(br1, misses_1, color='black', width=barWidth, edgecolor='grey', label=l1)
    br2 = [x + barWidth for x in br1]
    ax1.bar(br2, misses_2, color='grey', width=barWidth, edgecolor='grey', label=l2)
    br3 = [x + barWidth for x in br2]
    ax1.bar(br3, misses_3, color='blue', width=barWidth, edgecolor='grey', label=l3)
    
    if log: 
        ax1.set_yscale("log")

    # Show the number of the bar on top of it
    for i in range(len(misses_1)):
        ax1.text(i, misses_1[i], format_number(misses_1[i]), ha='center', va='bottom')
        ax1.text(i + barWidth, misses_2[i], format_number(misses_2[i]), ha='center', va='bottom')
        ax1.text(i + 2 * barWidth, misses_3[i], format_number(misses_3[i]), ha='center', va='bottom')
    
    ax1.set_yticklabels([format_number(y) for y in ax1.get_yticks()])
    flags = ['NONE', 'UNROLL', 'CACHE AWARE', 'UNROLL & CACHE AWARE', 'BEST']
    ax1.set_xticks([r + barWidth for r in range(len(misses_1))])
    ax1.set_xticklabels(flags, fontsize=16)
    
    fig.tight_layout()
    fig.legend(fontsize=16, loc='upper right')
    plt.title(title + "_" + stat, fontweight='bold', fontsize=30)
    plt.savefig('measurements/case_' + name + '_' + stat + '.svg', format='svg')
    plt.close()

plot_case('1', 'Matrix size test', 0, 1, '64', '512')
plot_case('2', 'Pattern size test', 2, 3, '32', '128')
plot_case('3', 'Number of patterns test', 4, 5, '8', '128')

# show a barplot for cache-misses , having one bar per test case per compile flag

plot_case_cache('', "", 1, 3, 5, 'matrix', 'pattern', 'pattern count', 'cache-misses', True)
plot_case_cache('', "", 1, 3, 5, 'matrix', 'pattern', 'pattern count', 'cache-references', True)

### worker plot
# worker_count,matsize,pattern_size,nb_patterns,transfers_per_sec,cache-misses,cache-references
# 1, ...
# 2, ...
# 3, ...

# compare the different worker counts on different aspects 
# 1. transfers per second
# 2. cache-misses / cache-references

fig, ax = plt.subplots(figsize =(12, 8))

ax_x = worker_results['worker_count'].unique()
# transfers per second
ax_y = worker_results.groupby('worker_count')['transfers_per_sec'].mean()
print(ax_y)
plt.plot(ax_x, ax_y, label='transfers per second', marker='o')

plt.xlabel('Worker count', fontweight ='bold', fontsize = 22)
plt.ylabel('Transfers per second', fontweight ='bold', fontsize = 22)
plt.legend(fontsize = 16)
plt.title('Worker count test', fontweight = 'bold', fontsize = 30)
plt.savefig('measurements/worker_count.svg', format='svg')

fig, ax = plt.subplots(figsize =(12, 8))

ax_x = worker_results['worker_count'].unique()
# cache-misses / cache-references
# example : "cache-misses": "1,000,203", "cache-references": "10,000"
ax_y = []
for index, row in worker_results.iterrows():
    hit_rate = float(row['cache-misses'].replace(",","")) / float(row['cache-references'].replace(",","")) * 100
    ax_y.append(round(hit_rate, 2))
    
print(ax_y)
plt.plot(ax_x, ax_y, label='cache-misses / cache-references', marker='o')

plt.xlabel('Worker count', fontweight ='bold', fontsize = 22)
plt.ylabel('Cache miss rate (%)', fontweight ='bold', fontsize = 22)
plt.legend(fontsize = 16)
plt.title('Worker count test', fontweight = 'bold', fontsize = 30)
plt.savefig('measurements/worker_count_cache.svg', format='svg')
plt.close()