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

generations = baseline_run1['generations']
baseline_run1_popmax = np.array(baseline_run1['best_fitness'])
baseline_run2_popmax = np.array(baseline_run2['best_fitness'])
baseline_run3_popmax = np.array(baseline_run3['best_fitness'])

# print(len(generations))

baseline_runs_popmaxes = np.vstack((baseline_run1_popmax, baseline_run2_popmax, baseline_run3_popmax))

baseline_means = baseline_runs_popmaxes.mean(axis=0)
baseline_stds = baseline_runs_popmaxes.std(axis=0, ddof=1)

fig, ax = plt.subplots()

# print(baseline_means)
fig.set_size_inches(8, 3.5)
fig.tight_layout()

ax.errorbar(generations, baseline_means, baseline_stds, linestyle="none", label="Baseline", marker='o', color='black', elinewidth=1, capsize=1, markersize=2)
# ax.plot(generations, baseline_means, color='black', alpha=0.75)
ax.fill_between(generations, baseline_means + baseline_stds, baseline_means - baseline_stds, color='black', alpha=0.2)
ax.set_xlabel("Generation")
ax.set_ylabel("Population Best Fitness")
fig.tight_layout()

plt.show()

