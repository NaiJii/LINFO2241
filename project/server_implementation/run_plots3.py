import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import os
if not os.path.exists('measurements'):
    os.makedirs('measurements')

plt.tight_layout()

results = pd.read_csv("performance_data.csv")

case1_x_pre = []
case1_y_pre = []
case1_x_aft = []
case1_y_aft = []

for index, row in results.iterrows():
    if index % 6 == 0:
        case1_x_pre.append(row['make_cmd'])
        case1_y_pre.append(row['time elapsed'])
    elif index % 6 == 1:
        case1_x_aft.append(row['make_cmd'])
        case1_y_aft.append(row['time elapsed'])


a = [2, 2, 2, 2]
b = [1, 1, 1, 1]

barWidth = 0.25
fig = plt.subplots(figsize =(12, 8)) 

br1 = np.arange(len(case1_y_pre)) 
br2 = [x + barWidth for x in br1]  

plt.bar(br1, case1_y_pre, color ='r', width = barWidth, 
        edgecolor ='grey', label ='Smaller matrix size') 

plt.bar(br2, case1_y_aft, color ='g', width = barWidth, 
        edgecolor ='grey', label ='Bigger matrix size') 

plt.ylim(0)

plt.xlabel('Compile flags', fontweight ='bold', fontsize = 15) 
plt.ylabel('Transfers per second', fontweight ='bold', fontsize = 15) 
plt.xticks([r + barWidth for r in range(len(case1_y_pre))], 
        ['DUNROLL', 'DCACHE AWARE', 'DBEST', 'DUNROLL and DCACHE AWARE'])

plt.legend()
plt.savefig('measurements/case1.svg', format='svg')
plt.title('case 1')
plt.show()