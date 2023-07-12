import math as m
import numpy as np
import json
import matplotlib.pyplot as plt

with open("./NEAT_RUN_STATS/figureinf-run-1.json", 'r') as f:
    inf_run1 = json.load(f)

with open("./NEAT_RUN_STATS/figureinf-run-2.json", 'r') as f:
    inf_run2 = json.load(f)

with open("./NEAT_RUN_STATS/figureinf-run-3.json", 'r') as f:
    inf_run3 = json.load(f)

generations = inf_run1['generations']
inf_run1_popmax = np.array(inf_run1['best_fitness'])
inf_run2_popmax = np.array(inf_run2['best_fitness'])
inf_run3_popmax = np.array(inf_run3['best_fitness'])
inf_runs_popmaxes = np.vstack((inf_run1_popmax, inf_run2_popmax, inf_run3_popmax))
inf_means = inf_runs_popmaxes.mean(axis=0)
inf_stds = inf_runs_popmaxes.std(axis=0, ddof=1)

with open("./NEAT_RUN_STATS/obstaclerun-run-1.json", 'r') as f:
    obst_run1 = json.load(f)

with open("./NEAT_RUN_STATS/obstaclerun-run-2.json", 'r') as f:
    obst_run2 = json.load(f)

with open("./NEAT_RUN_STATS/obstaclerun-run-3.json", 'r') as f:
    obst_run3 = json.load(f)

generations = obst_run1['generations']
obst_run1_popmax = np.array(obst_run1['best_fitness'])
obst_run2_popmax = np.array(obst_run2['best_fitness'])
obst_run3_popmax = np.array(obst_run3['best_fitness'])
obst_runs_popmaxes = np.vstack((obst_run1_popmax, obst_run2_popmax, obst_run3_popmax))
obst_means = obst_runs_popmaxes.mean(axis=0)
obst_stds = obst_runs_popmaxes.std(axis=0, ddof=1)

fig, (ax, ax2) = plt.subplots(2, 1, sharex=True, sharey=True)

fig.set_size_inches(8, 4.4)

ax.errorbar(generations, inf_means, inf_stds, linestyle="none", marker='o', color='black', elinewidth=1, capsize=1, markersize=2)
ax.fill_between(generations, inf_means + inf_stds, inf_means - inf_stds, hatch="//", color='black', alpha=0.4, label="'Infinity' track")
ax.legend()
ax.set_ylabel("Pop. Best Fitness")

ax2.errorbar(generations, obst_means, obst_stds, linestyle="none", marker='o', color='black', elinewidth=1, capsize=1, markersize=2)
ax2.fill_between(generations, obst_means + obst_stds, obst_means - obst_stds, hatch="\\\\", color='black', alpha=0.4, label="'Obstacle' track")
ax2.legend()
ax2.set_xlabel("Generation")
ax2.set_ylabel("Pop. Best Fitness")

fig.tight_layout()
plt.subplots_adjust(wspace=0)
plt.subplots_adjust(hspace=.0)
plt.show()