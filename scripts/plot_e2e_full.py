import matplotlib.pyplot as plt
import numpy as np

# Model and group setup
models = ['1B', '4B', '27B']
groups = ['Isolated','Time-slice', 'MPS', 'GM-Share']
# group_colors = ['skyblue', 'lightgreen', 'lightcoral']
group_colors = ['skyblue', 'lightgreen', 'plum', 'lightcoral']

# Timing data
init_times = {
    '1B': [0.725, 0.763, 0.763, 0.675],
    '4B': [1.038, 1.161, 1.162, 1.061],
    '27B': [3.396, 4.091, 4.024, 3.8]
}
decode_times = {
    '1B': [0.305, 0.281, 0.283, 0.359],
    '4B': [0.399, 0.389, 0.393, 0.442],
    '27B': [1.054, 1.217, 1.542, 0.988]
}

# # Timing data
# init_times = {
#     '1B': [0.763, 0.763, 0.675],
#     '4B': [1.161, 1.162, 1.061],
#     '27B': [4.091, 4.024, 3.8]
# }
# decode_times = {
#     '1B': [0.281, 0.283, 0.359],
#     '4B': [0.389, 0.393, 0.442],
#     '27B': [1.217, 1.542, 0.988]
# }

# # e2e_times = {
# #     '1B': [1.067, 1.028, 0.972],
# #     '4B': [1.619, 1.579, 1.414],
# #     '27B': [5.364, 5.519, 4.643]
# # }

x = np.arange(len(models))
# width = 0.2
# offsets = [-width, 0, width]
width = 0.2
offsets = [-1.5 * width, -0.5 * width, 0.5 * width, 1.5 * width]


# plt.style.use('seaborn-v0_8')
fig, ax = plt.subplots(figsize=(10, 6))

# Plot bars
for i, group in enumerate(groups):
    init = [init_times[model][i] for model in models]
    decode = [decode_times[model][i] for model in models]
    pos = x + offsets[i]
    ax.bar(pos, init, width, label=f'{group} Load', color=group_colors[i])
    ax.bar(pos, decode, width, bottom=init, label=f'{group} Decode', color=group_colors[i], alpha=0.6, hatch='/')

# Labels
ax.set_xlabel('Model Size', fontsize=16)
ax.set_ylabel('E2E Time (seconds)', fontsize=16)
# ax.set_title('Init and Decode Time Breakdown by Model and Group')
ax.set_xticks(x)
ax.set_xticklabels(models)

# Legend above the plot in a single row
# ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.15), ncol=3, fontsize='medium')
ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=4, fontsize=12)

plt.tight_layout()
plt.savefig('grouped_model_time_breakdown_top_legend.png', bbox_inches='tight')
plt.close()
