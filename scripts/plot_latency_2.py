import matplotlib.pyplot as plt
import numpy as np

# Setup
con_levels = ['5', '10', '15']
groups = ['Isolated', 'Time-slice', 'MPS', 'GM-Share']
colors = ['skyblue', 'lightgreen', 'plum', 'lightcoral']
model_sizes = ['1b', '4b', '27b']

# Data: [con5, con10, con15] for each model size
avg_times = {
    'Isolated': [[1.031, 1.031, 1.031], [1.437, 1.437, 1.437], [4.45, 4.45, 4.45]],
    'Time-slice': [[1.089, 1.044, 1.057], [1.566, 1.55, 1.557], [5.01, 5.308, 5.122]],
    'MPS': [[1.062, 1.047, 1.074], [1.513, 1.555, 1.584], [5.395, 5.567, 5.356]],
    'GM-Share': [[1.082, 1.034, 1.008], [1.533, 1.503, 1.472], [4.944, 4.787, 4.902]]
}

std_devs = {
    'Isolated': [[0.038, 0.038, 0.038], [0.044, 0.044, 0.044], [0.08, 0.08, 0.08]],
    'Time-slice': [[0.071, 0.067, 0.063], [0.089, 0.088, 0.082], [0.236, 0.422, 0.397]],
    'MPS': [[0.08, 0.071, 0.057], [0.1, 0.099, 0.103], [0.518, 0.585, 0.463]],
    'GM-Share': [[0.117, 0.127, 0.112], [0.194, 0.203, 0.164], [0.965, 0.768, 0.643]]
}

# Plotting one figure per model size
for model_idx, model in enumerate(model_sizes):
    x = np.arange(len(con_levels))
    width = 0.2

    fig, ax = plt.subplots(figsize=(8, 5))

    for i, group in enumerate(groups):
        means = [avg_times[group][model_idx][j] for j in range(len(con_levels))]
        errors = [std_devs[group][model_idx][j] for j in range(len(con_levels))]
        ax.bar(x + i * width - 1.5 * width, means, width,
               yerr=errors, label=group, color=colors[i], capsize=5)

    ax.set_xlabel('Load Level', fontsize=16)
    ax.set_ylabel('Total Time (s)', fontsize=16)
    # ax.set_title(f'Model Size: {model}', fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels(con_levels, fontsize=14)
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax.grid(False, axis='x')
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, 1.02), ncol=4, fontsize=14)

    plt.tight_layout()
    plt.savefig(f'total_latency_{model}.png', bbox_inches='tight')
    plt.close()
