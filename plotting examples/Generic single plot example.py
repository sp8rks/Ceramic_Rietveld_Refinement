import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

plt.rcParams['font.size']=14

# Check and set the current working directory
print("Current working directory:", os.getcwd())
os.chdir(os.path.dirname(__file__))
print("Changed working directory to:", os.getcwd())

filename = 'generic_single_plot.csv'
df = pd.read_csv(filename)

x = df['x'].dropna()
y = df['y'].dropna()

x2 = df['x2'].dropna()
y2 = df['y2'].dropna()

x3 = df['x3'].dropna()
y3 = df['y3'].dropna()

# bodacious colors
colors = sns.color_palette("rocket", 3) # personal fav 
colors = sns.color_palette("crest", 3) # also nice

# plot
fig = plt.figure(1, figsize=(5, 5))
plt.semilogx(x3, y3, linestyle='-', marker='^', label='ammonium perchlorate', color=colors[2], mfc='w', markersize=8) # plot data
plt.semilogx(x2, y2, linestyle='-', marker='s', label='iron oxide', color=colors[1], mfc='w', markersize=8) # plot data
plt.semilogx(x, y, linestyle='-', marker='o', label='aluminum', color=colors[0], mfc='w', markersize=8) # plot data

# plot params
plt.xlim([1, 1e4])
plt.ylim([-0.5, 16])
plt.minorticks_on()
plt.tick_params(direction='in', right=True, top=True)
plt.tick_params(labelsize=14)
plt.tick_params(labelbottom=True, labeltop=False, labelright=False, labelleft=True)
yticks = np.arange(0, 16.1, 4)

plt.tick_params(direction='in', which='minor', length=5, bottom=True, top=True, left=True, right=True)
plt.tick_params(direction='in', which='major', length=10, bottom=True, top=True, left=True, right=True)
plt.yticks(yticks)

plt.xlabel(r'particle radii ($\mu m$)', fontsize=14) 
plt.ylabel(r'percent contribution', fontsize=14)

plt.legend(fontsize=14)  # add the legend (will default to 'best' location)

plt.savefig('generic_plot.png', dpi=300, bbox_inches="tight")
