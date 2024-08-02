import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import matplotlib as mpl
import os

# Fix font to 14 and make it so it's editable PDF
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['font.size'] = 14

# Grab data
filename = r'G:\My Drive\teaching\workshop slides\Ceramic_Rietveld_Refinement\refinement examples\90Al2O3_10Si\refinement\histogram.csv'
df = pd.read_csv(filename)

# Pull data from CSV
x_data = df['Q'].dropna()
y_obs = df['y_obs'].dropna()
y_fit = df['y_calc'].dropna()
y_bkg = df['y_bkg'].dropna()
hkl1 = df['phase 1'].dropna()
hkl2 = df['phase 2'].dropna()

# Set the limits of the plot
xmin = 0.95  # adjust as needed
xmax = 5.5   # adjust as needed

# Generate Ram's color palette
seshadri = ['#c3121e', '#0348a1', '#ffb01c', '#027608', '#0193b0', '#9c5300', '#949c01', '#7104b5']

# Prepare multipanel plot 
fig = plt.figure(1, figsize=(5, 5))
gs = gridspec.GridSpec(15, 1)
gs.update(wspace=0.25, hspace=0.45)

# Generate main figure
xtr_subplot = fig.add_subplot(gs[2:15, 0:1])
plt.plot(x_data, y_obs, label='Experimental data', linestyle='none', 
         marker='o', color=seshadri[1], mfc='white', markersize=4)  # cerulean blue color
plt.plot(x_data, y_fit, label='Rietveld fit, R$_{wp}$=13%',  # adjust as needed
         linestyle='-', color=seshadri[2], linewidth=1)
plt.plot(x_data, y_bkg, label='Sample holder', linestyle='-', 
         color=seshadri[4], linewidth=1)
plt.plot(x_data, y_fit - y_obs - 1000, label='Difference', linestyle='-', 
         color='grey', linewidth=1)  # Difference curve shifted down by 1000 units

# Define ticks labels and legend
plt.tick_params(direction='in', right=True, top=True)
plt.tick_params(labelbottom=True, labeltop=False, labelright=False, labelleft=False)    
xticks = np.arange(0, 5.5, 1)  # adjust these as needed
yticks = np.arange(0, 13000, 4000)  # adjust these as needed
plt.minorticks_on()
plt.tick_params(direction='in', which='minor', length=5, bottom=True, top=True, left=True, right=True)
plt.tick_params(direction='in', which='major', length=10, bottom=True, top=True, left=True, right=True)
plt.xticks(xticks)
plt.yticks(yticks)
plt.xlabel(r'$Q\,(\AA^{-1})$') 
plt.ylabel('Intensity (arbitrary units)')  
plt.legend(fontsize=11)
plt.xlim(xmin, xmax)

# Label weight fractions of phases
plt.text(3.2, 6000, 'Al$_2$O$_3$=90wt%')  # adjust as needed
plt.text(3.2, 5000, 'Si=10wt%')  # adjust as needed

# HKL position plot for phase 1
xtr_subplot = fig.add_subplot(gs[0:1, 0:1])
for xc in hkl1.values:
    plt.axvline(x=xc, color='grey')

plt.tick_params(direction='in', bottom=False, right=True, top=False)
plt.tick_params(labelleft=False, labelbottom=False)
plt.xlim(xmin, xmax)
plt.text(5.6, 0.3, 'Al$_2$O$_3$')  # adjust as needed

# HKL position plot for phase 2
xtr_subplot = fig.add_subplot(gs[1:2, 0:1])
for xc in hkl2.values:
    plt.axvline(x=xc, color='grey')

plt.tick_params(direction='in', bottom=False, right=True, top=False)
plt.tick_params(labelleft=False, labelbottom=False)
plt.xlim(xmin, xmax)
plt.text(5.6, 0.3, 'Si')  # adjust as needed

# Ensure the directory exists before saving
output_dir = r'G:\My Drive\teaching\workshop slides\Ceramic_Rietveld_Refinement\plotting examples'
os.makedirs(output_dir, exist_ok=True)

# Export figure
plt.savefig(os.path.join(output_dir, 'XRD_Rietveld.png'), dpi=300, bbox_inches="tight")
