import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import matplotlib as mpl
import seaborn as sns
import os

mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['font.size'] = 14

# Set the working directory to the script's location
print("Current working directory:", os.getcwd())
os.chdir(os.path.dirname(__file__))
print("Changed working directory to:", os.getcwd())

# Grab dataset
filename = 'spectroscopy.csv'
df = pd.read_csv(filename)

# Downsample data to every 10th data point
df = df.iloc[::10, :]

# Pull data from CSV
x90 = df['X 90 Kohm'].dropna()
y90 = df['Y 90 Kohm'].dropna()
x90_clear = df['X 90 Kohm-clear'].dropna()
y90_clear = df['Y 90 Kohm-clear'].dropna()
x60 = df['X 60 Kohm'].dropna()
y60 = df['Y 60 Kohm'].dropna()
x60_clear = df['X 60 Kohm-clear'].dropna()
y60_clear = df['Y 60 Kohm-clear'].dropna()
x30 = df['X 30 Kohm'].dropna()
y30 = df['Y 30 Kohm'].dropna()
x30_clear = df['X 30 Kohm-clear'].dropna()
y30_clear = df['Y 30 Kohm-clear'].dropna()

# Set the limits of the plot for dataset1
xmin = 400
xmax = 800
ymin = 60
ymax = 120

# Generate some nice colors
seshadri = ['#c3121e', '#0348a1', '#ffb01c', '#027608', '#0193b0', '#9c5300', '#949c01', '#7104b5']
# Or try a color from seaborn
colors = sns.color_palette("rocket", 6)

# Prepare multipanel plot 
fig = plt.figure(1, figsize=(5, 5))
gs = gridspec.GridSpec(4, 4)
gs.update(wspace=0.2, hspace=0.25)

# Generate first panel
xtr_subsplot = fig.add_subplot(gs[0:4, 0:2])

# Plot data for left panel
plt.plot(x90, y90, linestyle='none', marker='^', label='90', 
         color=colors[0], mfc='w', markersize=8)
plt.plot(x60, y60, linestyle='none', marker='o', label='60', 
         color=colors[1], markerfacecolor='w', markersize=8)
plt.plot(x30, y30, linestyle='none', marker='s', label='30', 
         color=colors[2], markerfacecolor='w', markersize=8)

# Define where you want ticks
xticks = np.arange(0, (xmax+1), (xmax/4))
yticks = np.arange(ymin, (ymax+1), (ymax/4))

# or do xticks by hand if they don't look right
xticks = np.arange(300, 701, 200)
yticks = np.arange(60, 121, 20)

# Provide info on tick parameters
plt.minorticks_on()
plt.tick_params(direction='in', which='minor', length=5, 
                bottom=True, top=True, left=True, right=True)
plt.tick_params(direction='in', which='major', length=10, 
                bottom=True, top=True, left=True, right=True)
plt.xticks(xticks)
plt.yticks(yticks)

# Create a legend
plt.legend()

# Plot limits
plt.xlim(xmin, xmax)
plt.ylim(ymin, ymax)

# Create axes labels
plt.ylabel(r'Transparency % $\alpha$')
plt.text(645, 52, 'Wavelength (nm)')

# Generate second panel
xtr_subsplot = fig.add_subplot(gs[0:2, 2:4])
plt.plot(x90_clear, y90_clear, linestyle='none', marker='^', 
         label='90 clear', color=colors[3], mfc='w', markersize=8)
plt.plot(x60_clear, y60_clear, linestyle='none', marker='o', 
         label='60 clear', color=colors[4], mfc='w', markersize=8)
plt.plot(x30_clear, y30_clear, linestyle='none', marker='s', 
         label='30 clear', color=colors[5], mfc='w', markersize=8)

# Automatically set ticks
xticks = np.arange(0, (xmax+1), (xmax/4))
yticks = np.arange(ymin, (ymax+1), (ymax/4))
# or do xticks by hand if they don't look right
xticks = np.arange(100, 800, 200)
yticks = np.arange(60, 121, 20)

# Define tick parameters
plt.minorticks_on()
plt.tick_params(direction='in', which='minor', length=5, 
                bottom=True, top=True, left=True, right=True)
plt.tick_params(direction='in', which='major', length=10, 
                bottom=True, top=True, left=True, right=True)
plt.tick_params(labelbottom=False, labeltop=False, 
                labelright=True, labelleft=False)

plt.xticks(xticks)
plt.yticks(yticks)

# Set plot limits
plt.xlim(xmin, xmax)
plt.ylim(ymin, ymax)

plt.legend()

# Generate third panel
xtr_subsplot = fig.add_subplot(gs[2:4, 2:4])
plt.plot(x90_clear, y90_clear, linestyle='none', marker='^', 
         label='90 clear', color=colors[3], mfc='w', markersize=8)
plt.plot(x60_clear, y60_clear, linestyle='none', marker='o', 
         label='60 clear', color=colors[4], mfc='w', markersize=8)
plt.plot(x30_clear, y30_clear, linestyle='none', marker='s', 
         label='30 clear', color=colors[5], mfc='w', markersize=8)

# Automatically set ticks
xticks = np.arange(0, (xmax+1), (xmax/4))
yticks = np.arange(ymin, (ymax+1), (ymax/4))
# or do xticks by hand if they don't look right
xticks = np.arange(100, 800, 200)
yticks = np.arange(60, 121, 20)

# Define tick parameters
plt.minorticks_on()
plt.tick_params(direction='in', which='minor', length=5, 
                bottom=True, top=True, left=True, right=True)
plt.tick_params(direction='in', which='major', length=10, 
                bottom=True, top=True, left=True, right=True)
plt.tick_params(labelbottom=True, labeltop=False, 
                labelright=True, labelleft=False)

plt.xticks(xticks)
plt.yticks(yticks)

# Set plot limits
plt.xlim(xmin, xmax)
plt.ylim(ymin, ymax)

plt.legend()

# Export figure
plt.savefig('multi_panel_plot.png', dpi=300, bbox_inches="tight")
