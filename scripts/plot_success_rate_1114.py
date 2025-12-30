import matplotlib.pyplot as plt
import numpy as np

# Data
loads = ['Load 5', 'Load 10', 'Load 15']
methods = ['Time-slice', 'MPS', 'GM-Share']

# Original percentages
time_slice = [40.0, 36.1, 26.5]
mps = [40.0, 28.1, 26.8]
gm_share = [100.0, 100.0, 100.0]

# Normalize to GM-Share
time_slice_norm = [ts/gm*100 for ts, gm in zip(time_slice, gm_share)]
mps_norm = [mp/gm*100 for mp, gm in zip(mps, gm_share)]
gm_share_norm = [gm/gm*100 for gm in gm_share]  # always 100%

# Combine into array
data = np.array([time_slice_norm, mps_norm, gm_share_norm])

# Plot setup
x = np.arange(len(loads))
width = 0.25

fig, ax = plt.subplots(figsize=(8,3))

# Bars
ax.bar(x - width, data[0], width, label='Time-slice', color='skyblue')
ax.bar(x, data[1], width, label='MPS', color='lightgreen')
ax.bar(x + width, data[2], width, label='GM-Share', color='lightcoral')

# Labels and formatting
ax.set_ylabel('Normalized to GM-Share (%)')
# ax.set_title('Method Performance Normalized to GM-Share')
ax.set_xticks(x)
ax.set_xticklabels(loads)
ax.set_ylim(0, 110)
ax.legend()

# Add value labels
for i in range(len(loads)):
    ax.text(x[i] - width, data[0][i] + 2, f"{data[0][i]:.1f}%", ha='center')
    ax.text(x[i], data[1][i] + 2, f"{data[1][i]:.1f}%", ha='center')
    ax.text(x[i] + width, data[2][i] + 2, f"{data[2][i]:.1f}%", ha='center')

plt.tight_layout()
plt.savefig('success_rate_1114.png')
plt.close()

print("Plot saved as 'success_rate_1114.png'")

