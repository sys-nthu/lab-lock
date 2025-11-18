import subprocess
import time
import numpy as np
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

RUNS = 10

# Binaries
BIN_NAIVE  = "./sloppy-counter"
BIN_OPT    = "./sloppy-counter-opt"
BIN_ATOMIC = "./atomic-counter"
BIN_MUTEX  = "./mutex-counter"

# Settings
THRESHOLDS = [2, 4, 16]   # only for sloppy versions
WORKERS = [4, 8]

rows = []

# ------------------------------------------------------------
def run_once(binary, threshold=None, workers=4):
    cmd = [binary]

    if threshold is not None:
        cmd += [str(threshold), str(workers)]
    else:
        cmd += [str(workers)]

    start = time.time()
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return time.time() - start

def run_many(binary, threshold, workers):
    times = [run_once(binary, threshold, workers) for _ in range(RUNS)]
    arr = np.array(times)
    return np.median(arr)

def run_many_no_threshold(binary, workers):
    times = [run_once(binary, None, workers) for _ in range(RUNS)]
    arr = np.array(times)
    return np.median(arr)
# ------------------------------------------------------------

print("\nRunning benchmark...\n")

# Ensure results directory exists
results_dir = "results"
os.makedirs(results_dir, exist_ok=True)

for workers in WORKERS:

    # sloppy versions (have threshold)
    for th in THRESHOLDS:
        med = run_many(BIN_NAIVE, th, workers)
        rows.append([workers, str(th), "Baseline sloppy", med])

        med = run_many(BIN_OPT, th, workers)
        rows.append([workers, str(th), "Optimized sloppy", med])

    # atomic (no threshold)
    med = run_many_no_threshold(BIN_ATOMIC, workers)
    rows.append([workers, "N/A", "Atomic global", med])

    # mutex (no threshold)
    med = run_many_no_threshold(BIN_MUTEX, workers)
    rows.append([workers, "N/A", "Mutex global", med])


# ------------------------------------------------------------
# Create DataFrame
df = pd.DataFrame(rows, columns=["workers", "threshold", "version", "median"])

csv_path = os.path.join(results_dir, "benchmark_full.csv")
df.to_csv(csv_path, index=False)
print(f"CSV written: {csv_path}\n")

# ------------------------------------------------------------
# Visualization (Seaborn bar plot, NO error bars)
# ------------------------------------------------------------
sns.set_theme(style="whitegrid")

plt.figure(figsize=(7,5))

g = sns.catplot(
    data=df,
    kind="bar",
    x="threshold",
    y="median",
    hue="version",
    col="workers",
    height=5,
    aspect=1.1,
    palette="Set2"
)

# y-axis log scale
g.set(yscale="log")

g.set_axis_labels("Threshold", "Median Runtime (log-scale seconds)")
g.set_titles("Degree of Contention = {col_name}")
g.fig.suptitle("Full Sloppy Counter Benchmark (Bar Plot, No Error Bars)", y=1.05)

plot_path = os.path.join(results_dir, "benchmark_full_plot.png")
plt.savefig(plot_path, dpi=150)
print(f"Plot saved: {plot_path}\n")

plt.show()
