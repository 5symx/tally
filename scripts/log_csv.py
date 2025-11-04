import csv
import statistics
import re

def summarize(group, name):
    mean = round(statistics.mean(group), 3)
    stdev = round(statistics.stdev(group), 3) if len(group) > 1 else 0
    print(f"{name}: Count={len(group)}, Avg={mean}s, Std Dev={stdev}s")
    return mean

def extract_init_times(csv_path):
    init_times = []
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if 'init_time' in row and row['init_time']:
                try:
                    init_times.append(float(row['init_time']))
                except ValueError:
                    continue
    return init_times

def extract_decode_times(csv_path):
    decode_times = []
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if 'decode_time' in row and row['decode_time']:
                try:
                    decode_times.append(float(row['decode_time']))
                except ValueError:
                    continue
    return decode_times


def extract_speed(csv_path):
    speeds = []
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if 'speed' in row and row['speed']:
                try:
                    speeds.append(float(row['speed']))
                except ValueError:
                    continue
    return speeds

def extract_total_times(csv_path):
    total_times = []
    with open(csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                init = float(row['init_time']) if row.get('init_time') else 0.0
                decode = float(row['decode_time']) if row.get('decode_time') else 0.0
                total_times.append(init + decode)
            except ValueError:
                continue  # Skip rows with invalid numeric values
    return total_times


# # File paths
# count = 10
# model = 1

# naive_csv = f'./result/naive-con{count}-{model}b.csv'
# mps_csv   = f'./result/mps-con{count}-{model}b.csv'
# gms_csv   = f'./result/gm-con{count}-{model}b.csv'

# print("Using files:")
# print("Naive:", naive_csv)
# print("MPS:", mps_csv)
# print("GMS:", gms_csv)

# # Extract init_time values
# group_naive = extract_decode_times(naive_csv)
# group_mps = extract_decode_times(mps_csv)
# group_gms = extract_decode_times(gms_csv)

# # Summarize
# mean_naive = summarize(group_naive, "Group naive")
# mean_mps = summarize(group_mps, "Group mps")
# mean_gms = summarize(group_gms, "Group gms")

# # Calculate percentage increase
# increase_percent = ((mean_naive - mean_gms) / mean_naive) * 100
# print(f"Group naive's init_time is {increase_percent:.2f}% higher than Group gms's.")

# increase_percent = ((mean_mps - mean_gms) / mean_mps) * 100
# print(f"Group mps's init_time is {increase_percent:.2f}% higher than Group gms's.")



# ideal print
naive_csv = './result/naive-con1-1b.csv'
group_naive = extract_decode_times(naive_csv)
mean_naive = summarize(group_naive, "Group ideal")

# # File paths
# naive_csv = './result/naive-con5-1b.csv'
# mps_csv = './result/mps-con5-1b.csv'
# gms_csv = './result/gm-con5-1b.csv'