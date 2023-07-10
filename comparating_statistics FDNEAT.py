import math as m
import numpy as np
import matplotlib.pyplot as plt
import json


with open("./NEAT_RUN_STATS/silverstone-base-run-1.json", 'r') as f:
    baseline_run1 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-base-run-2.json", 'r') as f:
    baseline_run2 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-base-run-3.json", 'r') as f:
    baseline_run3 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-FDNEAT-run-1.json", 'r') as f:
    FDNEAT_run1 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-FDNEAT-run-2.json", 'r') as f:
    FDNEAT_run2 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-FDNEAT-run-3.json", 'r') as f:
    FDNEAT_run3 = json.load(f)

generations = baseline_run1['generations']
baseline_run1_popmax = np.array(baseline_run1['best_fitness'])
baseline_run2_popmax = np.array(baseline_run2['best_fitness'])
baseline_run3_popmax = np.array(baseline_run3['best_fitness'])
FDNEAT_run1_popmax = np.array(FDNEAT_run1['best_fitness'])
FDNEAT_run2_popmax = np.array(FDNEAT_run2['best_fitness'])
FDNEAT_run3_popmax = np.array(FDNEAT_run3['best_fitness'])

# print(len(generations))

baseline_runs_popmaxes = np.vstack((baseline_run1_popmax, baseline_run2_popmax, baseline_run3_popmax))
FDNEAT_runs_popmaxes = np.vstack((FDNEAT_run1_popmax, FDNEAT_run2_popmax, FDNEAT_run3_popmax))

baseline_means = baseline_runs_popmaxes.mean(axis=0)
baseline_stds = baseline_runs_popmaxes.std(axis=0, ddof=1)

FDNEAT_means = FDNEAT_runs_popmaxes.mean(axis=0)
FDNEAT_stds = FDNEAT_runs_popmaxes.std(axis=0, ddof=1)

fig, ax = plt.subplots()

# print(baseline_means)
fig.set_size_inches(8, 3.5)
fig.tight_layout()

baseline_errorbar = ax.errorbar(generations, baseline_means, baseline_stds, linestyle="none", marker='o', color='black', elinewidth=1, capsize=1, markersize=2)
FDNEAT_errorbar = ax.errorbar(generations, FDNEAT_means, FDNEAT_stds, linestyle="none", marker='o', color='black', elinewidth=1, capsize=1, markersize=2)
FDNEAT_errorbar[-1][0].set_linestyle('--')
# ax.plot(generations, baseline_means, color='black', alpha=0.75)
ax.fill_between(generations, baseline_means + baseline_stds, baseline_means - baseline_stds, color='black', alpha=0.2, label="Baseline")
ax.fill_between(generations, FDNEAT_means + FDNEAT_stds, FDNEAT_means - FDNEAT_stds, color='black', alpha=0.5, hatch="\\\\", label="FDNEAT")
ax.set_xlabel("Generation")
ax.set_ylabel("Population Best Fitness")
ax.legend()
fig.tight_layout()

plt.show()

