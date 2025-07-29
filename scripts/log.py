import re
import json
import statistics

# Patterns for separate components
model_pattern = re.compile(r"Model size:\s*(?P<model_size>\d+b)")
init_pattern = re.compile(r"init ctx load initialize finish in (?P<init_time>\d+\.\d+) s")
decode_pattern = re.compile(r"main: decoded (?P<tokens>\d+) tokens in (?P<decode_time>\d+\.\d+) s, speed: (?P<speed>\d+\.\d+) t/s")
finish_pattern = re.compile(r"Tally server shutting down ...")

def extract_split_log_entries(log_file_path):
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
                # temp = init_match.groupdict()
            elif decode_match and temp:
                temp.update(decode_match.groupdict())
                results.append(temp)
                temp = {}  # reset for next pair
            elif finish_match:
                temp = {}
                results.append(temp)
                temp = {}


    return results

# Example usage
log_path = "./txt-naive-12b.log"
entries = extract_split_log_entries(log_path)

# for entry in entries:
#     print(entry)

group1 = []
group2 = []

### naive


prev_empty = False
for idx, entry in enumerate(entries):
    # print(entry)

    if entry == {}:
        prev_empty = True
        continue

    try:
        init_time = float(entry.get('init_time', 0))
    except (ValueError, TypeError):
        continue
    
    group2.append(init_time)
    if len(group2) == 10:
        break

    # if not group1:
    #     group1.append(init_time)
    # elif prev_empty:
    #     group1.append(init_time)
    #     prev_empty = False
    # else:
    #     group2.append(init_time)

# Statistics helper
def summarize(group, name):
    mean = round(statistics.mean(group), 3)
    stdev = round(statistics.stdev(group), 3) if len(group) > 1 else 0
    print(f"{name}: Count={len(group)}, Avg={mean}s, Std Dev={stdev}s")
    # print(f"{name}: Count={len(group)}, Avg={mean}t/s, Std Dev={stdev}t/s")
    return mean

# Results
# mean1 = summarize(group1, "Group 1")
mean2 = summarize(group2, "Group 2")

# Calculate percentage increase
# increase_percent = ((mean1 - mean2) / mean1) * 100

# Print result rounded to two decimals
# print(f"Group 1's init_time is {increase_percent:.2f}% higher than Group 2's.")

# increase_percent = ((mean2 - mean1) / mean1) * 100

# print(f"Group 1's speed is {increase_percent:.2f}% higher than Group 2's.")

#### TMM
print()


# Example usage
log_path = "./txt-fr3-12b.log"
entries = extract_split_log_entries(log_path)

# for entry in entries:
#     print(entry)

group1 = []
group2 = []

prev_empty = False
for idx, entry in enumerate(entries):
    # print(entry)

    if entry == {}:
        prev_empty = True
        continue

    try:
        init_time = float(entry.get('init_time', 0))
    except (ValueError, TypeError):
        continue

    

    if not group1:
        group1.append(init_time)
    elif prev_empty:
        group1.append(init_time)
        prev_empty = False
    else:
        group2.append(init_time)
    if len(group1) == 50:
        break

# Statistics helper
def summarize(group, name):
    mean = round(statistics.mean(group), 3)
    stdev = round(statistics.stdev(group), 3) if len(group) > 1 else 0
    print(f"{name}: Count={len(group)}, Avg={mean}s, Std Dev={stdev}s")
    # print(f"{name}: Count={len(group)}, Avg={mean}t/s, Std Dev={stdev}t/s")
    return mean

# Results
mean1 = summarize(group1, "Group 1")
mean2 = summarize(group2, "Group 2")


# Calculate percentage increase
increase_percent = ((mean1 - mean2) / mean1) * 100

# Print result rounded to two decimals
print(f"Group 1's init_time is {increase_percent:.2f}% higher than Group 2's.")

# increase_percent = ((mean2 - mean1) / mean1) * 100

# print(f"Group 1's speed is {increase_percent:.2f}% higher than Group 2's.")