import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


data = pd.read_pickle("/Users/rdchlcap/repos/lzmst/tool_output_data/pendleton2-30yrBathys.pkl")  
print('Pendleton 30yr Run Slopes:', data['slopes_by70thTransect'])
print('Pendleton 30yr run Slopes mean:', np.mean(data['slopes_by70thTransect']))


data = pd.read_pickle("/Users/rdchlcap/repos/lzmst/tool_output_data/pendleton2Bathys.pkl")  
print('Pendleton 1yr Run Slopes:', data['slopes_by70thTransect'])
print('Pendleton 1yr run Slopes mean:', np.mean(data['slopes_by70thTransect']))


data = pd.read_pickle("/Users/rdchlcap/repos/lzmst/tool_output_data/pendleton30yrBathys.pkl")  
print('Pendleton 30yr run Slopes:', data['slopes_by70thTransect'])
print('Pendleton 30yr run Slopes mean:', np.mean(data['slopes_by70thTransect']))
print('transects')
print(len(data['whitewater_crossshore_distances_byTransect']))

### Mayport

data = pd.read_pickle("/Users/rdchlcap/repos/lzmst/tool_output_data/mayportBathys.pkl")  
print('Mayport Slopes:', data['slopes_by70thTransect'])

data = pd.read_pickle("/Users/rdchlcap/repos/lzmst/tool_output_data/cleanedtransectsmayportBathys.pkl")  
print('Mayport Slopes 2:', data['slopes_by70thTransect'])
print('transects')
print(len(data['whitewater_crossshore_distances_byTransect']))

## Camp Lejeune
data = pd.read_pickle("/Users/rdchlcap/repos/lzmst/tool_output_data/lejeuene30yr.pkl")  
print('lejeuene Slopes:', data['slopes_by70thTransect'])

# print('transects')
# print(len(data['whitewater_crossshore_distances_byTransect']))
# print(data['whitewater_crossshore_distances_byTransect'])
