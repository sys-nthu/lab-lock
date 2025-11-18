import subprocess
import time
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

RUNS = 10

BIN_ATOMIC = "./atomic-counter"
BIN_MUTEX  = "./mutex-counter"

WORKERS = [1, 2, 4, 8]

rows = []

# Ensure results directory exists
results_dir = "results"
os.makedirs(results_dir, exist_ok=True)

# ------------------------------------------------------------
def run_once(binary, workers):
    cmd = [binary, str(workers)]
    start = time.time()
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return time.time() - start

def run_many(binary, workers):
    times = [run_once(binary, workers) for _ in range(RUNS)]
    arr = np.array(times)
    return np.median(arr)
# ------------------------------------------------------------

print("\nRunning atomic vs mutex benchmark...\n")

for workers in WORKERS:

    med_atomic = run_many(BIN_ATOMIC, workers)
    rows.append([workers, "Atomic global", med_atomic])

    med_mutex = run_many(BIN_MUTEX, workers)
    rows.append([workers, "Mutex global", med_mutex])

# ------------------------------------------------------------
# Create DataFrame
df = pd.DataFrame(rows, columns=["workers", "version", "median"])

csv_path = os.path.join(results_dir, "benchmark_atomic_mutex.csv")
df.to_csv(csv_path, index=False)
print(f"CSV saved to {csv_path}\n")

# ------------------------------------------------------------
# Visualization
# ------------------------------------------------------------
sns.set_theme(style="whitegrid")

sns.barplot(
    data=df,
    x="workers",
    y="median",
    hue="version",
    palette="Set2"
)

plt.title("Atomic vs Mutex Counter Performance")
plt.xlabel("Degree of Contention")
plt.ylabel("Median Runtime (seconds)")
plt.yscale("log")  # optional: remove if you prefer linear
plt.tight_layout()

plot_path = os.path.join(results_dir, "benchmark_atomic_mutex_plot.png")
plt.savefig(plot_path, dpi=150)
print(f"Plot saved as {plot_path}\n")

plt.show()
