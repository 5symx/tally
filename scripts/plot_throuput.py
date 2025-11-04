import matplotlib.pyplot as plt

# Model labels
models = ['1B', '4B', '27B']

# Original throughput values
group_0 = [98.003, 73.552, 20.309]
group_mps = [103.003, 78.137, 20.958]
group_2 = [81.991, 71.962, 29.776]

# Normalize to Group 0
normalized_mps = [m / g0 for m, g0 in zip(group_mps, group_0)]
normalized_2 = [g2 / g0 for g2, g0 in zip(group_2, group_0)]
baseline = [1.0] * len(models)

# Plot setup
# plt.style.use('seaborn-v0_8')
fig, ax = plt.subplots(figsize=(8, 5))

# Plot lines
ax.plot(models, normalized_mps, 'o--', label='MPS', color='lightgreen')
ax.plot(models, normalized_2, 'o--', label='GM-Share', color='lightcoral')
# ax.plot(models, baseline, 'o--', label='Naive', color='skyblue')
ax.axhline(y=1.0, color='black', linestyle='dotted', linewidth=1, label='Time-slice')

# Labels and formatting
ax.set_xlabel('Model Size', fontsize=18)
ax.set_ylabel('Normalized Throughput', fontsize=18)
# ax.set_title('Normalized Throughput Comparison by Model')
ax.set_ylim(0.8, 1.8)
ax.legend(fontsize=16)

# ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=6, fontsize='medium')

plt.tight_layout()
plt.savefig('normalized_throughput_with_baseline.png')
plt.close()

print("Plot saved as 'normalized_throughput_with_baseline.png'")


# throughput = {
#     '1B': [101.952, 107.886, 90.392],
#     '4B': [71.67, 74.658, 73.427],
#     '27B': [22.825, 21.008, 30.967]
# }
