import matplotlib.pyplot as plt
import numpy as np

# Group labels
groups = ['0 (naive)', 'mps', '2']

# Decode and Init times
# 27b
decode_times = [1.365, 1.533, 0.969]
init_times = [3.999, 3.986, 3.674]

# decode_times = [1.0, 1.123, 0.710]
# init_times = [1.0, 0.997, 0.919]


# # 4b
decode_times = [0.422, 0.404, 0.417]
init_times = [1.197, 1.175, 0.997]

# decode_times = [1.0, 0.957, 0.988]
# init_times = [1.0, 0.982, 0.833]


# 1b
init_times = [0.771, 0.75, 0.634]
decode_times = [0.296, 0.278, 0.338]

# init_times = [1.0, 0.972, 0.822]
# decode_times = [1.0, 0.939, 1.142]



# Bar positions
x = np.arange(len(groups))
width = 0.6

# Plot setup
# plt.style.use('seaborn-v0_8')
fig, ax = plt.subplots(figsize=(8, 6))

# Plot init time (bottom)
bars_init = ax.bar(x, init_times, width, label='Init Time', color='skyblue')

# Plot decode time (stacked on top)
bars_decode = ax.bar(x, decode_times, width, bottom=init_times, label='Decode Time', color='salmon')

# Labels and title
ax.set_xlabel('Group')
ax.set_ylabel('Total E2E Time (seconds)')
ax.set_title('End-to-End Time Breakdown by Group')
ax.set_xticks(x)
ax.set_xticklabels(groups)
ax.legend()

# Save the figure
plt.tight_layout()
plt.savefig('e2e_time_breakdown_updated_4b.png')
plt.close()

print("Plot saved as 'e2e_time_breakdown_updated.png'")

# fig, ax = plt.subplots(figsize=(8, 6))

# # Plot decode time (bottom)
# bars_decode = ax.bar(x, decode_times, width, label='Decode Time', color='salmon')

# # Plot init time (stacked on top)
# bars_init = ax.bar(x, init_times, width, bottom=decode_times, label='Init Time', color='skyblue')

# # Labels and title
# ax.set_xlabel('Group')
# ax.set_ylabel('E2E Time (seconds)')
# ax.set_title('End-to-End Time Breakdown by Group')
# ax.set_xticks(x)
# ax.set_xticklabels(groups)
# ax.legend()

# # Save the figure
# plt.tight_layout()
# plt.savefig('e2e_time_breakdown_stacked_27b.png')
# plt.close()

# print("Plot saved as 'e2e_time_breakdown_stacked.png'")
