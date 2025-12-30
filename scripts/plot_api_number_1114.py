import matplotlib.pyplot as plt
import numpy as np

# Data
apis = ['cudaMalloc', 'cudaMemset', 'cudaMemcpyAsync', 'cudaStreamSynchronize', 'cudaFree']
total_calls = [9, 157, 1274, 1580, 9]
reusable_calls = [1, 157, 340, 340, 1]

# Compute non-reusable calls
non_reusable_calls = [t - r for t, r in zip(total_calls, reusable_calls)]

# Compute percentages (normalized to 100%)
reusable_pct = [r / t * 100 for r, t in zip(reusable_calls, total_calls)]
non_reusable_pct = [nr / t * 100 for nr, t in zip(non_reusable_calls, total_calls)]

# Plot
x = np.arange(len(apis))
width = 0.6

fig, ax = plt.subplots(figsize=(8,3))

# 100% stacked bars
ax.bar(x, reusable_pct, width, label='Reusable-related', color='skyblue')
ax.bar(x, non_reusable_pct, width, bottom=reusable_pct, label='Non-reusable', color='lightcoral')

# Labels and formatting
ax.set_ylabel('Percentage (%)')
# ax.set_title('CUDA API Reusable-related Calls (100% stacked)')
ax.set_xticks(x)
ax.set_xticklabels(apis, rotation=30, ha='right')
ax.set_ylim(0, 100)
ax.legend()

# Add percentage labels
for i in range(len(apis)):
    ax.text(x[i], reusable_pct[i]/2, f"{reusable_pct[i]:.1f}%", ha='center', va='center', color='black')
    ax.text(x[i], reusable_pct[i] + non_reusable_pct[i]/2, f"{non_reusable_pct[i]:.1f}%", ha='center', va='center', color='black')


plt.tight_layout()
plt.savefig('cuda_numbers_1114.png')
plt.close()

print("Plot saved as 'cuda_numbers_1114.png'")

# plt.tight_layout()
# plt.show()
