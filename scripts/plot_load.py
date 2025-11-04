import matplotlib.pyplot as plt
import numpy as np

# Init times for each group: [1B, 4B, 27B]
group_0 = np.array([0.763, 1.161, 4.091])
group_mps = np.array([0.763, 1.162, 4.024])
group_2 = np.array([0.675, 1.061, 3.8])

# Calculate speedup relative to Group 0
speedup_mps = group_0 / group_mps
speedup_2 = group_0 / group_2

# Model labels
models = ['1B', '4B', '27B']
x = np.arange(len(models))

# plt.style.use('seaborn-v0_8')
fig, ax = plt.subplots(figsize=(8, 5))

# Plot speedup lines
ax.plot(x, speedup_mps, marker='o', linestyle='--', label='MPS', color='lightgreen')
ax.plot(x, speedup_2, marker='s', linestyle='--', label='GM-Share', color='lightcoral')

# Baseline line at y = 1.0
ax.axhline(y=1.0, color='black', linestyle='dotted', linewidth=1, label='Time-slice')

# Formatting
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=16)
ax.set_xlabel('Model Size', fontsize=18)
ax.set_ylabel('Latency Speedup', fontsize=18)
# ax.set_title('Latency Speedup for Init Times Relative to Group 0')
ax.set_ylim(0.9, 1.2)
ax.legend(fontsize=16)
# ax.grid(True)

plt.tight_layout()
plt.savefig('latency_speedup_plot.png')
plt.close()

print("Plot saved as 'latency_speedup_plot.png'")

# # Formatting
# ax.set_xticks(x)
# ax.set_xticklabels(models)
# ax.set_xlabel('Model')
# ax.set_ylabel('Latency Speedup')
# # ax.set_title('Latency Speedup for Init Times Relative to Group 0')
# ax.set_ylim(1, 1.4)
# ax.legend()
# # ax.grid(True)

# plt.tight_layout()
# plt.savefig('latency_speedup_plot.png')
# plt.close()


# throughput = {
#     '1B': [101.952, 107.886, 90.392],
#     '4B': [71.67, 74.658, 73.427],
#     '27B': [22.825, 21.008, 30.967]
# }
