# import matplotlib.pyplot as plt
# import numpy as np

# # Data
# models = ['1B', '4B', '12B', '27B']
# naive = [0.774, 1.199, 2.695, 4.022]
# non_tmm = [0.775, 1.324, 2.739, 5.499]
# tmm = [0.634, 0.997, 2.001, 3.674]

# x = np.arange(len(models))
# width = 0.25

# # Plotting
# plt.figure(figsize=(8, 5))
# plt.bar(x - width, naive, width, label='Naïve', color='#1f77b4')
# plt.bar(x, non_tmm, width, label='Non-TMM', color='#ff7f0e')
# plt.bar(x + width, tmm, width, label='TMM', color='#2ca02c')

# # Labeling
# plt.xlabel('Model Size', fontsize=12)
# plt.ylabel('Overhead (s)', fontsize=12)
# plt.title('Overhead Comparison Across Model Sizes', fontsize=14)
# plt.xticks(x, models)
# plt.legend()
# plt.grid(axis='y', linestyle='--', alpha=0.6)

# # Layout for publication aesthetics
# plt.tight_layout()
# plt.savefig('overhead_comparison.png', dpi=300)
# plt.show()


# ----------------------
# import matplotlib.pyplot as plt
# import numpy as np

# # Raw data
# models = ['1B', '4B', '27B']
# naive = np.array([0.774, 1.199, 4.022])
# non_tmm = np.array([0.775, 1.324, 5.499])
# tmm = np.array([0.634, 0.997, 3.674])

# # Normalization: divide each method by naive
# # non_tmm_norm = non_tmm / naive
# tmm_norm = tmm / naive
# naive_norm = naive / naive  # this will be a vector of ones
# print(tmm_norm)

# x = np.arange(len(models))
# width = 0.25

# # Plotting
# plt.figure(figsize=(8, 5))
# plt.bar(x - width/2, naive_norm, width, label='Naïve', color='#1f77b4')

# plt.bar(x + width/2, tmm_norm, width, label='TMM', color='#ff7f0e')
# # plt.bar(x, non_tmm_norm, width, label='Non-TMM', color='#2ca02c')

# # Labeling
# plt.xlabel('Model Size', fontsize=12)
# # Update title and y-axis label to reflect latency
# plt.ylabel('Latency for Workload Switching (s)', fontsize=12)
# plt.title('Normalized Latency Comparison Across Model Sizes', fontsize=14)
# plt.xticks(x, models)
# plt.legend()
# plt.grid(axis='y', linestyle='--', alpha=0.6)

# # Layout for publication quality
# plt.tight_layout()
# plt.savefig('normalized_overhead_comparison.png', dpi=300)
# plt.show()


# ## ----------------------
# import matplotlib.pyplot as plt
# import numpy as np

# # Raw data
# models = ['1B', '4B', '27B']
# naive = np.array([0.774, 1.199, 4.022])
# tmm = np.array([0.634, 0.997, 3.674])

# # Normalization
# naive_norm = naive / naive
# tmm_norm = tmm / naive

# x = np.arange(len(models))
# width = 0.25

# # Plotting
# fig, ax = plt.subplots(figsize=(8, 5))
# bars_naive = ax.bar(x - width/2, naive_norm, width, label='Naïve', color='#1f77b4')
# bars_tmm = ax.bar(x + width/2, tmm_norm, width, label='TMM', color='#ff7f0e')

# # # Add value labels on top of each bar
# # ax.bar_label(bars_naive, fmt='%.2f', padding=3, fontsize=10)
# ax.bar_label(bars_tmm, fmt='%.2f', padding=3, fontsize=10)

# # Axis labels and title
# ax.set_xlabel('Model Size', fontsize=12)
# ax.set_ylabel('Normalized Latency for Workload Switching', fontsize=12)
# ax.set_title('Normalized Latency Comparison Across Model Sizes', fontsize=14)
# ax.set_xticks(x)
# ax.set_xticklabels(models)
# # ax.legend()
# ax.grid(axis='y', linestyle='--', alpha=0.6)

# # Layout for publication
# plt.tight_layout()
# plt.savefig('normalized_latency_labels.png', dpi=300)

import matplotlib.pyplot as plt
import numpy as np

# Raw data
models = ['1B', '4B', '27B']
naive = np.array([0.774, 1.199, 4.022])
tmm = np.array([0.634, 0.997, 3.674])

# Normalization
naive_norm = naive / naive
tmm_norm = tmm / naive

# Speed-up (Naïve / TMM)
speedup = (naive - tmm) / naive * 100

x = np.arange(len(models))
width = 0.25

# Main plot
fig, ax = plt.subplots(figsize=(8, 5))


bars_naive = ax.bar(x - width/2, naive_norm, width, label='Naïve', color='#1f77b4')
bars_tmm = ax.bar(x + width/2, tmm_norm, width, label='TMM', color='#ff7f0e')
# ax.bar_label(bars_tmm, fmt='%.2f', padding=3, fontsize=10)

# Primary axis labels
ax.set_xlabel('Model Size', fontsize=12)
ax.set_ylabel('Normalized Latency for Workload Switching', fontsize=12)
ax.set_title('Switching Latency Comparison with Speed-Up Overlay', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.grid(axis='y', linestyle='--', alpha=0.6)

# Secondary axis for speed-up
ax2 = ax.twinx()
ax2.plot(x, speedup, marker='s', color='#333333', linestyle='--', linewidth=2)
ax2.set_ylabel('Speed-Up Percentage(%)', fontsize=12)
ax2.set_ylim(0, 50)  # adjust as needed for clarity

# Optional: Add speed-up values as text above points
for i in range(len(x)):
    ax2.text(x[i], speedup[i]+3, f'{speedup[i]:.2f}%', ha='center', va='bottom', fontsize=10, color='#333333')

# Legends
ax.legend(loc='upper left', fontsize=10)

# Layout for publication
plt.tight_layout()
plt.savefig('normalized_latency_speedup_overlay.png', dpi=300)
plt.show()