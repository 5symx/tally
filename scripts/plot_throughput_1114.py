import matplotlib.pyplot as plt
import numpy as np

# Data
models = ['1B', '4B', '27B']
groups = ['Isolated','Time-slice', 'MPS', 'GM-Share']
# group_colors = ['skyblue', 'lightgreen', 'plum', 'lightcoral']
group_colors = ['#4784B8', '#BFE2FF', '#FFECB3', '#FFA500', '#D8BFD8',  '#FFB6C1']  #'#FFA500', '#FFECB3',

isolated = [98.339, 74.995, 28.425]
time_slice = [98.003, 73.552, 20.309]
mps = [103.003, 78.137, 20.958]
gm_share = [81.991, 71.962, 29.776]

data = np.array([isolated, time_slice, mps, gm_share])

# Normalization (higher throughput is better)
normalized = (data / isolated) * 100

# Plot setup
x = np.arange(len(models))
width = 0.2

fig, ax1 = plt.subplots(figsize=(8,4))

# Left axis: throughput bars
for i, (method, color) in enumerate(zip(groups, group_colors)):
    ax1.bar(x + (i-1.5)*width, data[i], width, label=method, color=color)

ax1.set_ylabel('Throughput (tokens/s)')
ax1.set_xticks(x)
ax1.set_xticklabels(models)
# ax1.set_title('Throughput vs Normalized Percentage (baseline = Isolated)')
ax1.legend(loc='upper left')

# # Right axis: normalized percentages
# ax2 = ax1.twinx()
# for i, (method, color) in enumerate(zip(groups, group_colors)):
#     ax2.plot(x, normalized[i], marker='o', color=color, linestyle='--')

# ax2.set_ylabel('Normalized to Isolated (%)')
# # Default auto-scale (no fixed 0–105 range)
# ax2.set_ylim(0, 110)  # <- removed to "change back"

# Right axis: normalized percentages
ax2 = ax1.twinx()
# Plot only Time-slice, MPS, GM-Share (skip Isolated line)
for i, (method, color) in enumerate(zip(groups[1:], group_colors[1:])):
    ax2.plot(x, normalized[i+1], marker='o', color=color, linestyle='--', label=f'{method} norm')

# Add fixed horizontal baseline line at 100%
ax2.axhline(100, color='gray', linestyle=':', linewidth=1.5, label='Baseline (100%)')

ax2.set_ylabel('Normalized to Isolated (%)')
ax2.set_ylim(0, max(normalized[1:].max(), 110))  # auto-scale with some headroom


plt.tight_layout()
plt.savefig('normalized_throughput_with_baseline_1114.png')
plt.close()

print("Plot saved as 'normalized_throughput_with_baseline_1114.png'")


# plt.tight_layout()
# plt.show()
