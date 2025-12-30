import matplotlib.pyplot as plt
import numpy as np

# Data
models = ['1B', '4B', '27B']
groups = ['Isolated','Time-slice', 'MPS', 'GM-Share']
# group_colors = ['skyblue', 'lightgreen', 'plum', 'lightcoral']
group_colors = ['#4784B8', '#BFE2FF', '#FFECB3', '#FFA500', '#D8BFD8',  '#FFB6C1']

# Latency values (seconds)
init_times = {
    '1B': [0.725, 0.763, 0.763, 0.675],
    '4B': [1.038, 1.161, 1.162, 1.061],
    '27B': [3.396, 4.091, 4.024, 3.8]
}

# Convert to array for easier handling
data = np.array([init_times[m] for m in models]).T  # shape (4 methods, 3 workloads)

# Normalization (lower latency is better)
# Formula: (Isolated / Method) * 100
isolated = data[0]
normalized = (isolated / data) * 100

# Plot setup
x = np.arange(len(models))
width = 0.2

fig, ax1 = plt.subplots(figsize=(8,4))

# Left axis: latency bars
for i, (method, color) in enumerate(zip(groups, group_colors)):
    ax1.bar(x + (i-1.5)*width, data[i], width, label=method, color=color)

ax1.set_ylabel('Execution Latency (s)')
ax1.set_xticks(x)
ax1.set_xticklabels(models)
# ax1.set_title('Latency vs Normalized Efficiency (baseline = Isolated)')
ax1.legend(loc='upper left')

# # Right axis: normalized percentages
# ax2 = ax1.twinx()
# for i, (method, color) in enumerate(zip(groups, group_colors)):
#     ax2.plot(x, normalized[i], marker='o', color=color, linestyle='--')

# ax2.set_ylabel('Normalized to Isolated (%)')
# # Auto-scale (no fixed 0–105 range)
# ax2.set_ylim(0, 110)  # uncomment if you want to cap at 105%



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
plt.savefig('normalized_latency_with_baseline_1114.png')
plt.close()

print("Plot saved as 'normalized_latency_with_baseline_1114.png'")


# plt.tight_layout()
# plt.show()
