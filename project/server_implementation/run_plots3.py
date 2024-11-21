import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import os
if not os.path.exists('measurements'):
    os.makedirs('measurements')

plt.tight_layout()

results = pd.read_csv("performance_data.csv")

def plot_case(name, n1, n2, pre_ledger, aft_ledger):

    case_y_pre = []
    case_y_aft = []

    for index, row in results.iterrows():
        if index % 6 == n1:
            case_y_pre.append(row['transfers_per_sec'])
        elif index % 6 == n2:
            case_y_aft.append(row['transfers_per_sec'])

    barWidth = 0.25
    fig = plt.subplots(figsize =(12, 8)) 

    br1 = np.arange(len(case_y_pre)) 
    br2 = [x + barWidth for x in br1]  

    plt.bar(br1, case_y_pre, color ='r', width = barWidth, 
            edgecolor ='grey', label = pre_ledger) 

    plt.bar(br2, case_y_aft, color ='g', width = barWidth, 
            edgecolor ='grey', label = aft_ledger) 

    #plt.ylim(0)

    plt.yscale("log")

    plt.xlabel('Compile flags', fontweight ='bold', fontsize = 15) 
    plt.ylabel('Transfers per second', fontweight ='bold', fontsize = 15) 
    plt.xticks([r + barWidth for r in range(len(case_y_pre))], 
            ['DUNROLL', 'DCACHE AWARE', 'DBEST', 'DUNROLL and DCACHE AWARE'])

    plt.legend()
    plt.savefig('measurements/case1.svg', format='svg')
    plt.title('name')
    plt.show()

#plot_case('case 1', 0, 1, 'Smaller matrix size', 'Bigger matrix size')
#plot_case('case 2', 2, 3, 'Smaller pattern size', 'Bigger pattern size')
plot_case('case 3', 4, 5, 'Smaller amount of patterns', 'Larger amount of patterns')