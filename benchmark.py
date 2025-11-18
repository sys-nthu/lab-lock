import subprocess
import csv
import time
import math
import os
import matplotlib.pyplot as plt

# sweep thresholds 1, 2, 4, ..., 128
thresholds = [2**i for i in range(8)]  # 1..128

naive_bin = "./sloppy-counter"
opt_bin   = "./sloppy-counter-opt"

results = []

# Ensure results directory exists
results_dir = "results"
os.makedirs(results_dir, exist_ok=True)

print("Running benchmark...\n")
print(f"{'THRESH':>8}   {'NAIVE (s)':>12}   {'OPT (s)':>12}")

for th in thresholds:
    # --- run naive version ---
    t0 = time.time()
    subprocess.run([naive_bin, str(th)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    naive_time = time.time() - t0

    # --- run optimized version ---
    t0 = time.time()
    subprocess.run([opt_bin, str(th)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    opt_time = time.time() - t0

    results.append((th, naive_time, opt_time))

    print(f"{th:>8}   {naive_time:12.6f}   {opt_time:12.6f}")

# --- Write CSV ---
csv_path = os.path.join(results_dir, "sloppy_benchmark.csv")
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["threshold", "naive_time", "opt_time"])
    writer.writerows(results)

print(f"\nCSV written to {csv_path}")

# --- Plot the benchmark ---
plt.figure(figsize=(8,5))
plt.plot(thresholds, [r[1] for r in results], marker='o', label="Naive (false sharing)")
plt.plot(thresholds, [r[2] for r in results], marker='o', label="Optimized (no false sharing)")

plt.xscale("log", base=2)
plt.xlabel("Flush threshold (log2 scale)")
plt.ylabel("Execution time (seconds)")
plt.title("Sloppy Counter Benchmark")
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)

plot_path = os.path.join(results_dir, "sloppy_benchmark.png")
plt.savefig(plot_path, dpi=150)

print(f"Plot saved to {plot_path}")
print("\nDone.")
