import subprocess
import csv
import time
import numpy as np
import os
import matplotlib.pyplot as plt

# Sweep threshold values: 1,2,4,...,128
thresholds = [2**i for i in range(8)]

# Worker counts to benchmark
workers_list = [2, 4, 8, 16]

# Binaries
naive_bin = "./sloppy-counter"
opt_bin   = "./sloppy-counter-opt"

RUNS = 20

def run_benchmark(binary, threshold, workers):
    """Run the binary multiple times and collect runtimes."""
    times = []
    for _ in range(RUNS):
        start = time.time()
        subprocess.run([binary, str(threshold), str(workers)],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        times.append(time.time() - start)
    return np.array(times)


# Ensure results directory exists
results_dir = "results"
os.makedirs(results_dir, exist_ok=True)

# CSV output
csv_path = os.path.join(results_dir, "sloppy_benchmark_workers.csv")
csv_file = open(csv_path, "w", newline="")
writer = csv.writer(csv_file)

writer.writerow([
    "workers", "threshold",
    "naive_median", "naive_p25", "naive_p75",
    "opt_median",   "opt_p25",   "opt_p75"
])

print("\nRunning worker-based benchmark...\n")

for workers in workers_list:
    print(f"\n### Workers = {workers} ###\n")
    print(f"{'THRESH':>8}   {'naive(med)':>12}   {'opt(med)':>12}")

    # figure for this worker-count
    plt.figure(figsize=(10,6))

    naive_medians = []
    naive_p25s = []
    naive_p75s = []

    opt_medians = []
    opt_p25s = []
    opt_p75s = []

    for th in thresholds:
        # Naive
        naive_times = run_benchmark(naive_bin, th, workers)
        naive_med = np.median(naive_times)
        naive_p25 = np.percentile(naive_times, 25)
        naive_p75 = np.percentile(naive_times, 75)

        # Opt
        opt_times = run_benchmark(opt_bin, th, workers)
        opt_med = np.median(opt_times)
        opt_p25 = np.percentile(opt_times, 25)
        opt_p75 = np.percentile(opt_times, 75)

        naive_medians.append(naive_med)
        naive_p25s.append(naive_p25)
        naive_p75s.append(naive_p75)

        opt_medians.append(opt_med)
        opt_p25s.append(opt_p25)
        opt_p75s.append(opt_p75)

        writer.writerow([
            workers, th,
            naive_med, naive_p25, naive_p75,
            opt_med,   opt_p25,   opt_p75
        ])

        print(f"{th:>8}   {naive_med:12.6f}   {opt_med:12.6f}")

    # Error bar calculation
    naive_lower = np.array(naive_medians) - np.array(naive_p25s)
    naive_upper = np.array(naive_p75s) - np.array(naive_medians)

    opt_lower = np.array(opt_medians) - np.array(opt_p25s)
    opt_upper = np.array(opt_p75s) - np.array(opt_medians)

    # Plot
    plt.errorbar(
        thresholds, naive_medians,
        yerr=[naive_lower, naive_upper],
        fmt='-o', capsize=6,
        label="Naive (false sharing)"
    )
    plt.errorbar(
        thresholds, opt_medians,
        yerr=[opt_lower, opt_upper],
        fmt='-o', capsize=6,
        label="Optimized (no false sharing)"
    )

    plt.xscale("log", base=2)
    plt.xlabel("Flush threshold (log₂ scale)")
    plt.ylabel("Execution time (seconds)")
    plt.title(f"Sloppy Counter Benchmark (workers = {workers})")
    plt.grid(True, linestyle='--', alpha=0.4)
    plt.legend()

    plot_path = os.path.join(results_dir, f"sloppy_benchmark_workers_{workers}.png")
    plt.savefig(plot_path, dpi=150)
    print(f"Plot saved to {plot_path}")

csv_file.close()
print(f"\nCSV saved to {csv_path}\n")
print("Done.")
