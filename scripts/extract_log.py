import os
import re
import csv

# Patterns for separate components
model_pattern = re.compile(r"Model size:\s*(?P<model_size>\d+b)")
init_pattern = re.compile(r"init ctx load initialize finish in (?P<init_time>\d+\.\d+) s")
decode_pattern = re.compile(r"main: decoded (?P<tokens>\d+) tokens in (?P<decode_time>\d+\.\d+) s, speed: (?P<speed>\d+\.\d+) t/s")
finish_pattern = re.compile(r"Tally server shutting down ...")

def extract_split_log_entries(log_file_path, count_value):
    results = []
    temp = {}

    with open(log_file_path, 'r') as f:
        for line in f:
            model_match = model_pattern.search(line)
            init_match = init_pattern.search(line)
            decode_match = decode_pattern.search(line)
            finish_match = finish_pattern.search(line)

            if model_match:
                temp = model_match.groupdict()
            elif init_match:
                temp.update(init_match.groupdict())
            elif decode_match and temp:
                temp.update(decode_match.groupdict())
                temp["count"] = count_value
                results.append(temp)
                temp = {}
            elif finish_match:
                temp = {}
                results.append(temp)
                temp = {}

    return results

# Directories
log_dir = "./updated_1029"
csv_dir = "./result"
os.makedirs(csv_dir, exist_ok=True)

# Process each .log file
for filename in os.listdir(log_dir):
    if filename.endswith(".log"):
        log_path = os.path.join(log_dir, filename)

        # Extract count from filename (e.g., naive-con10-1b.log → 10)
        count_match = re.search(r"con(\d+)-", filename)
        count_value = int(count_match.group(1)) if count_match else 0

        entries = extract_split_log_entries(log_path, count_value)

        csv_filename = os.path.splitext(filename)[0] + ".csv"
        csv_path = os.path.join(csv_dir, csv_filename)

        with open(csv_path, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["model_size", "init_time", "tokens", "decode_time", "speed", "count"])
            writer.writeheader()
            for entry in entries:
                if entry:
                    writer.writerow(entry)

        print(f"Processed: {filename} → {csv_filename} with count {count_value}")


# import re
# import csv
# import os

# # Patterns for separate components
# model_pattern = re.compile(r"Model size:\s*(?P<model_size>\d+b)")
# init_pattern = re.compile(r"init ctx load initialize finish in (?P<init_time>\d+\.\d+) s")
# decode_pattern = re.compile(r"main: decoded (?P<tokens>\d+) tokens in (?P<decode_time>\d+\.\d+) s, speed: (?P<speed>\d+\.\d+) t/s")
# finish_pattern = re.compile(r"Tally server shutting down ...")

# def extract_split_log_entries(log_file_path):
#     results = []
#     temp = {}

#     with open(log_file_path, 'r') as f:
#         for line in f:
#             model_match = model_pattern.search(line)
#             init_match = init_pattern.search(line)
#             decode_match = decode_pattern.search(line)
#             finish_match = finish_pattern.search(line)

#             if model_match:
#                 temp = model_match.groupdict()
#             elif init_match:
#                 temp.update(init_match.groupdict())
#             elif decode_match and temp:
#                 temp.update(decode_match.groupdict())
#                 results.append(temp)
#                 temp = {}  # reset for next entry
#             elif finish_match:
#                 temp = {}
#                 results.append(temp)
#                 temp = {}

#     return results

# # Extract entries

# log_dir = "./updated_1029"
# csv_dir = "./result"
# os.makedirs(csv_dir, exist_ok=True)

# # Process each .log file
# for filename in os.listdir(log_dir):
#     if filename.endswith(".log"):
#         log_path = os.path.join(log_dir, filename)
#         entries = extract_split_log_entries(log_path)

#         csv_filename = os.path.splitext(filename)[0] + ".csv"
#         csv_path = os.path.join(csv_dir, csv_filename)

#         with open(csv_path, mode='w', newline='') as file:
#             writer = csv.DictWriter(file, fieldnames=["model_size", "init_time", "tokens", "decode_time", "speed"])
#             writer.writeheader()
#             for entry in entries:
#                 if entry:
#                     writer.writerow(entry)

#         print(f"Processed: {filename} → {csv_filename}")

# log_path = "./updated_1029/naive-con1-1b.log"
# entries = extract_split_log_entries(log_path)

# # Write to CSV
# csv_file = "./result/naive-con1-1b.csv"
# with open(csv_file, mode='w', newline='') as file:
#     writer = csv.DictWriter(file, fieldnames=["model_size", "init_time", "tokens", "decode_time", "speed"])
#     writer.writeheader()
#     for entry in entries:
#         if entry:  # skip empty entries
#             writer.writerow(entry)

# print(f"CSV file '{csv_file}' created with {len(entries)} entries.")
