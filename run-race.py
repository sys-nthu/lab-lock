import subprocess
import re
import numpy as np
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

WORKERS = [1, 2, 4, 6, 8]
RUNS_PER_WORKER = 100
ITERS = 100000

pattern = re.compile(r"counter\s*=\s*(\d+)")

rows = []

# Ensure results directory exists
results_dir = "results"
os.makedirs(results_dir, exist_ok=True)

def run_race_counter(workers):
    """Run race-counter once and extract the final counter value."""
    cmd = ["./race-counter", str(workers)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)

    final_val = None

    for line in proc.stdout:
        m = pattern.search(line)
        if m:
            final_val = int(m.group(1))

    return final_val

print("\nCollecting race-condition deviation data...\n")

for w in WORKERS:
    expected = w * ITERS
    deviations = []

    print(f"Testing workers = {w} ...")

    for _ in range(RUNS_PER_WORKER):
        actual = run_race_counter(w)
        dev = actual - expected
        deviations.append(dev)

    deviations = np.array(deviations)
    med = np.median(deviations)
    p25 = np.percentile(deviations, 25)
    p75 = np.percentile(deviations, 75)

    rows.append([w, med, p25, p75])

# Create DataFrame
df = pd.DataFrame(rows, columns=["workers", "median_dev", "p25_dev", "p75_dev"])

csv_path = os.path.join(results_dir, "race_deviation.csv")
df.to_csv(csv_path, index=False)
print(f"Saved {csv_path}\n")

# -------------------------
# PLOT: single bar chart
# -------------------------
sns.set_theme(style="whitegrid")

# plt.figure(figsize=(8, 5))

plt.bar(
    df["workers"].astype(str),
    df["median_dev"],
    yerr=[df["median_dev"] - df["p25_dev"],
          df["p75_dev"] - df["median_dev"]],
    capsize=5,
    color="skyblue",
    edgecolor="black"
)

plt.xlabel("Workers")
plt.ylabel("Median Deviation")
plt.title("Race Condition: Deviation vs Worker Count")
plt.tight_layout()

plot_path = os.path.join(results_dir, "race_deviation_plot.png")
plt.savefig(plot_path, dpi=150)
print(f"Saved {plot_path}\n")

plt.show()
