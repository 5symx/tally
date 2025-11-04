import matplotlib.pyplot as plt
import numpy as np

# Data setup
model_sizes = ['1b', '4b', '27b']
groups = ['ideal', 'naive', 'mps', 'gms']
# colors = ['#4daf4a', '#377eb8', '#ff7f00', '#e41a1c']
colors = ['skyblue', 'lightgreen', 'plum', 'lightcoral']


# Average total times - con5
avg_times = {
    'ideal': [1.031, 1.437, 4.45],
    'naive': [1.089, 1.566, 5.01],
    'mps': [1.062, 1.513, 5.395],
    'gms': [1.082, 1.533, 4.944]
}

# Standard deviations
std_devs = {
    'ideal': [0.038, 0.044, 0.08],
    'naive': [0.071, 0.089, 0.236],
    'mps': [0.08, 0.1, 0.518],
    'gms': [0.117, 0.194, 0.965]
}

# # Average total times - con10
# avg_times = {
#     'ideal': [1.031, 1.437, 4.45],
#     'naive': [1.044, 1.55, 5.308],
#     'mps': [1.047, 1.555, 5.567],
#     'gms': [1.034, 1.503, 4.787]
# }

# # Standard deviations
# std_devs = {
#     'ideal': [0.038, 0.044, 0.08],
#     'naive': [0.067, 0.088, 0.422],
#     'mps': [0.071, 0.099, 0.585],
#     'gms': [0.127, 0.203, 0.768]
# }

# # Average total times - con15
# avg_times = {
#     'ideal': [1.031, 1.437, 4.45],
#     'naive': [1.057, 1.557, 5.122],
#     'mps': [1.074, 1.584, 5.356],
#     'gms': [1.008, 1.472, 4.902]
# }

# # Standard deviations
# std_devs = {
#     'ideal': [0.038, 0.044, 0.08],
#     'naive': [0.063, 0.082, 0.397],
#     'mps': [0.057, 0.103, 0.463],
#     'gms': [0.112, 0.164, 0.643]
# }

# Plotting
x = np.arange(len(model_sizes))
width = 0.2

# plt.style.use('seaborn-v0_8')
fig, ax = plt.subplots(figsize=(10, 6))

for i, group in enumerate(groups):
    ax.bar(x + i*width - 1.5*width, avg_times[group], width,
           yerr=std_devs[group], label=group, color=colors[i], capsize=5)

ax.set_xlabel('Model Size', fontsize=16)
ax.set_ylabel('Total Time (s)', fontsize=16)
# ax.set_title('Average Total Time by Model Size and Method', fontsize=14)
ax.set_xticks(x)
ax.set_xticklabels(model_sizes, fontsize=14)
# ax.legend(title='Method')
ax.grid(True, axis='y', linestyle='--', alpha=0.7)
ax.grid(False, axis='x')
# plt.tight_layout()
# plt.show()

# Legend above the plot in a single row
# ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.15), ncol=3, fontsize='medium')
ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=6, fontsize=14, title_fontsize=15)

plt.tight_layout()
plt.savefig('total_latency_con5.png', bbox_inches='tight')
plt.close()




# # Average init times - con5
# avg_times = {
#     'ideal': [0.725, 1.038, 3.396],
#     'naive': [0.782, 1.158, 3.497],
#     'mps': [0.769, 1.129, 3.887],
#     'gms': [0.706, 1.103, 3.929]
# }

# # Standard deviations
# std_devs = {
#     'ideal': [0.038, 0.048, 0.072],
#     'naive': [0.054, 0.093, 0.154],
#     'mps': [0.065, 0.101, 0.345],
#     'gms': [0.052, 0.131, 0.879]
# }

# # Plotting
# x = np.arange(len(model_sizes))
# width = 0.2

# plt.style.use('seaborn-v0_8')
# fig, ax = plt.subplots(figsize=(10, 6))

# for i, group in enumerate(groups):
#     ax.bar(x + i*width - 1.5*width, avg_times[group], width,
#            yerr=std_devs[group], label=group, color=colors[i], capsize=5)

# ax.set_xlabel('Model Size', fontsize=12)
# ax.set_ylabel('Init Time (s)', fontsize=12)
# ax.set_title('Average Init Time by Model Size and Method', fontsize=14)
# ax.set_xticks(x)
# ax.set_xticklabels(model_sizes)
# ax.legend(title='Method')
# ax.grid(True, axis='y', linestyle='--', alpha=0.7)

# plt.tight_layout()
# plt.show()
