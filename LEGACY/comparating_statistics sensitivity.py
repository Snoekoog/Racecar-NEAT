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

generations = baseline_run1['generations'][:20]
baseline_run1_popmax = np.array(baseline_run1['best_fitness'][:20])
baseline_run2_popmax = np.array(baseline_run2['best_fitness'][:20])
baseline_run3_popmax = np.array(baseline_run3['best_fitness'][:20])
baseline_runs_popmaxes = np.vstack((baseline_run1_popmax, baseline_run2_popmax, baseline_run3_popmax))
baseline_means = baseline_runs_popmaxes.mean(axis=0)
baseline_stds = baseline_runs_popmaxes.std(axis=0, ddof=1)

with open("./NEAT_RUN_STATS/silverstone-4species-run-1.json", 'r') as f:
    species4_run1 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-4species-run-2.json", 'r') as f:
    species4_run2 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-4species-run-3.json", 'r') as f:
    species4_run3 = json.load(f)

# generations = baseline_run1['generations']
species4_run1_popmax = np.array(species4_run1['best_fitness'])
species4_run2_popmax = np.array(species4_run2['best_fitness'])
species4_run3_popmax = np.array(species4_run3['best_fitness'])
species4_runs_popmaxes = np.vstack((species4_run1_popmax, species4_run2_popmax, species4_run3_popmax))
species4_means = species4_runs_popmaxes.mean(axis=0)
species4_stds = species4_runs_popmaxes.std(axis=0, ddof=1)

with open("./NEAT_RUN_STATS/silverstone-8species-run-1.json", 'r') as f:
    species8_run1 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-8species-run-2.json", 'r') as f:
    species8_run2 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-8species-run-3.json", 'r') as f:
    species8_run3 = json.load(f)

# generations = baseline_run1['generations']
species8_run1_popmax = np.array(species8_run1['best_fitness'])
species8_run2_popmax = np.array(species8_run2['best_fitness'])
species8_run3_popmax = np.array(species8_run3['best_fitness'])
species8_runs_popmaxes = np.vstack((species8_run1_popmax, species8_run2_popmax, species8_run3_popmax))
species8_means = species8_runs_popmaxes.mean(axis=0)
species8_stds = species8_runs_popmaxes.std(axis=0, ddof=1)

with open("./NEAT_RUN_STATS/silverstone-30pop-run-1.json", 'r') as f:
    pop30_run1 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-30pop-run-2.json", 'r') as f:
    pop30_run2 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-30pop-run-3.json", 'r') as f:
    pop30_run3 = json.load(f)

# generations = baseline_run1['generations']
pop30_run1_popmax = np.array(pop30_run1['best_fitness'])
pop30_run2_popmax = np.array(pop30_run2['best_fitness'])
pop30_run3_popmax = np.array(pop30_run3['best_fitness'])
pop30_runs_popmaxes = np.vstack((pop30_run1_popmax, pop30_run2_popmax, pop30_run3_popmax))
pop30_means = pop30_runs_popmaxes.mean(axis=0)
pop30_stds = pop30_runs_popmaxes.std(axis=0, ddof=1)

with open("./NEAT_RUN_STATS/silverstone-50pop-run-1.json", 'r') as f:
    pop50_run1 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-50pop-run-2.json", 'r') as f:
    pop50_run2 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-50pop-run-3.json", 'r') as f:
    pop50_run3 = json.load(f)

# generations = baseline_run1['generations']
pop50_run1_popmax = np.array(pop50_run1['best_fitness'])
pop50_run2_popmax = np.array(pop50_run2['best_fitness'])
pop50_run3_popmax = np.array(pop50_run3['best_fitness'])
pop50_runs_popmaxes = np.vstack((pop50_run1_popmax, pop50_run2_popmax, pop50_run3_popmax))
pop50_means = pop50_runs_popmaxes.mean(axis=0)
pop50_stds = pop50_runs_popmaxes.std(axis=0, ddof=1)

with open("./NEAT_RUN_STATS/silverstone-ts5-run-1.json", 'r') as f:
    ts5_run1 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-ts5-run-2.json", 'r') as f:
    ts5_run2 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-ts5-run-3.json", 'r') as f:
    ts5_run3 = json.load(f)

# generations = baseline_run1['generations']
ts5_run1_popmax = np.array(ts5_run1['best_fitness'])
ts5_run2_popmax = np.array(ts5_run2['best_fitness'])
ts5_run3_popmax = np.array(ts5_run3['best_fitness'])
ts5_runs_popmaxes = np.vstack((ts5_run1_popmax, ts5_run2_popmax, ts5_run3_popmax))
ts5_means = ts5_runs_popmaxes.mean(axis=0)
ts5_stds = ts5_runs_popmaxes.std(axis=0, ddof=1)

with open("./NEAT_RUN_STATS/silverstone-ts7-run-1.json", 'r') as f:
    ts7_run1 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-ts7-run-2.json", 'r') as f:
    ts7_run2 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-ts7-run-3.json", 'r') as f:
    ts7_run3 = json.load(f)

# generations = baseline_run1['generations']
ts7_run1_popmax = np.array(ts7_run1['best_fitness'])
ts7_run2_popmax = np.array(ts7_run2['best_fitness'])
ts7_run3_popmax = np.array(ts7_run3['best_fitness'])
ts7_runs_popmaxes = np.vstack((ts7_run1_popmax, ts7_run2_popmax, ts7_run3_popmax))
ts7_means = ts7_runs_popmaxes.mean(axis=0)
ts7_stds = ts7_runs_popmaxes.std(axis=0, ddof=1)

with open("./NEAT_RUN_STATS/silverstone-addnode6-run-1.json", 'r') as f:
    addnode6_run1 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-addnode6-run-2.json", 'r') as f:
    addnode6_run2 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-addnode6-run-3.json", 'r') as f:
    addnode6_run3 = json.load(f)

# generations = baseline_run1['generations']
addnode6_run1_popmax = np.array(addnode6_run1['best_fitness'])
addnode6_run2_popmax = np.array(addnode6_run2['best_fitness'])
addnode6_run3_popmax = np.array(addnode6_run3['best_fitness'])
addnode6_runs_popmaxes = np.vstack((addnode6_run1_popmax, addnode6_run2_popmax, addnode6_run3_popmax))
addnode6_means = addnode6_runs_popmaxes.mean(axis=0)
addnode6_stds = addnode6_runs_popmaxes.std(axis=0, ddof=1)

with open("./NEAT_RUN_STATS/silverstone-addnode9-run-1.json", 'r') as f:
    addnode9_run1 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-addnode9-run-2.json", 'r') as f:
    addnode9_run2 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-addnode9-run-3.json", 'r') as f:
    addnode9_run3 = json.load(f)

# generations = baseline_run1['generations']
addnode9_run1_popmax = np.array(addnode9_run1['best_fitness'])
addnode9_run2_popmax = np.array(addnode9_run2['best_fitness'])
addnode9_run3_popmax = np.array(addnode9_run3['best_fitness'])
addnode9_runs_popmaxes = np.vstack((addnode9_run1_popmax, addnode9_run2_popmax, addnode9_run3_popmax))
addnode9_means = addnode9_runs_popmaxes.mean(axis=0)
addnode9_stds = addnode9_runs_popmaxes.std(axis=0, ddof=1)

with open("./NEAT_RUN_STATS/silverstone-wm40-run-1.json", 'r') as f:
    wm40_run1 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-wm40-run-2.json", 'r') as f:
    wm40_run2 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-wm40-run-3.json", 'r') as f:
    wm40_run3 = json.load(f)

# generations = baseline_run1['generations']
wm40_run1_popmax = np.array(wm40_run1['best_fitness'])
wm40_run2_popmax = np.array(wm40_run2['best_fitness'])
wm40_run3_popmax = np.array(wm40_run3['best_fitness'])
wm40_runs_popmaxes = np.vstack((wm40_run1_popmax, wm40_run2_popmax, wm40_run3_popmax))
wm40_means = wm40_runs_popmaxes.mean(axis=0)
wm40_stds = wm40_runs_popmaxes.std(axis=0, ddof=1)

with open("./NEAT_RUN_STATS/silverstone-wm60-run-1.json", 'r') as f:
    wm60_run1 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-wm60-run-2.json", 'r') as f:
    wm60_run2 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-wm60-run-3.json", 'r') as f:
    wm60_run3 = json.load(f)

# generations = baseline_run1['generations']
wm60_run1_popmax = np.array(wm60_run1['best_fitness'])
wm60_run2_popmax = np.array(wm60_run2['best_fitness'])
wm60_run3_popmax = np.array(wm60_run3['best_fitness'])
wm60_runs_popmaxes = np.vstack((wm60_run1_popmax, wm60_run2_popmax, wm60_run3_popmax))
wm60_means = wm60_runs_popmaxes.mean(axis=0)
wm60_stds = wm60_runs_popmaxes.std(axis=0, ddof=1)

fig, (ax, ax2, ax3, ax4, ax5) = plt.subplots(5, 1, sharex=True, sharey=True)

# print(baseline_means)
fig.set_size_inches(8, 10.4)

first_hatch = ""
second_hatch = ""
third_hatch = ""
first_color = "black"
second_color = "darkblue"
third_color = "darkred"
first_alpha = 0.5
second_alpha = 0.2
third_alpha = 0.2

baseline_errorbar_1 = ax.errorbar(generations, baseline_means, baseline_stds, linestyle="none", marker='o', color=first_color, elinewidth=1, capsize=1, markersize=2)
species4_errorbar = ax.errorbar(generations, species4_means, species4_stds, linestyle="none", marker='o', color=second_color, elinewidth=1, capsize=1, markersize=2)
species8_errorbar = ax.errorbar(generations, species8_means, species8_stds, linestyle="none", marker='o', color=third_color, elinewidth=1, capsize=1, markersize=2)
species4_errorbar[-1][0].set_linestyle('--')
species8_errorbar[-1][0].set_linestyle('--')
ax.fill_between(generations, baseline_means + baseline_stds, baseline_means - baseline_stds, color=first_color, alpha=first_alpha, hatch=first_hatch, label="species target 6 (BL)")
ax.fill_between(generations, species4_means + species4_stds, species4_means - species4_stds, color=second_color, alpha=second_alpha, hatch=second_hatch, label="Species target 4")
ax.fill_between(generations, species8_means + species8_stds, species8_means - species8_stds, color=third_color, alpha=third_alpha, hatch=third_hatch, label="Species target 8")
ax.set_xlabel("Generation")
ax.set_ylabel("Pop. Best Fitness")
ax.legend()

baseline_errorbar_2 = ax2.errorbar(generations, baseline_means, baseline_stds, linestyle="none", marker='o', color=first_color, elinewidth=1, capsize=1, markersize=2)
pop30_errorbar = ax2.errorbar(generations, pop30_means, pop30_stds, linestyle="none", marker='o', color=second_color, elinewidth=1, capsize=1, markersize=2)
pop50_errorbar = ax2.errorbar(generations, pop50_means, pop50_stds, linestyle="none", marker='o', color=third_color, elinewidth=1, capsize=1, markersize=2)
pop30_errorbar[-1][0].set_linestyle('--')
pop50_errorbar[-1][0].set_linestyle('--')
ax2.fill_between(generations, baseline_means + baseline_stds, baseline_means - baseline_stds, color=first_color, hatch=first_hatch, alpha=first_alpha, label="Population size 40 (BL)")
ax2.fill_between(generations, pop30_means + pop30_stds, pop30_means - pop30_stds, color=second_color, alpha=second_alpha, hatch=second_hatch, label="Population size 30")
ax2.fill_between(generations, pop50_means + pop50_stds, pop50_means - pop50_stds, color=third_color, alpha=third_alpha, hatch=third_hatch, label="Population size 50")
ax2.set_xlabel("Generation")
ax2.set_ylabel("Pop. Best Fitness")
ax2.legend()

baseline_errorbar_3 = ax3.errorbar(generations, baseline_means, baseline_stds, linestyle="none", marker='o', color=first_color, elinewidth=1, capsize=1, markersize=2)
ts5_errorbar = ax3.errorbar(generations, ts5_means, ts5_stds, linestyle="none", marker='o', color=second_color, elinewidth=1, capsize=1, markersize=2)
ts7_errorbar = ax3.errorbar(generations, ts7_means, ts7_stds, linestyle="none", marker='o', color=third_color, elinewidth=1, capsize=1, markersize=2)
ts5_errorbar[-1][0].set_linestyle('--')
ts7_errorbar[-1][0].set_linestyle('--')
ax3.fill_between(generations, baseline_means + baseline_stds, baseline_means - baseline_stds, color=first_color, hatch=first_hatch, alpha=first_alpha, label="Tournament size 3 (BL)")
ax3.fill_between(generations, ts5_means + ts5_stds, ts5_means - ts5_stds, color=second_color, alpha=second_alpha, hatch=second_hatch, label="Tournament size 5")
ax3.fill_between(generations, ts7_means + ts7_stds, ts7_means - ts7_stds, color=third_color, alpha=third_alpha, hatch=third_hatch, label="Tournament size 7")
ax3.set_xlabel("Generation")
ax3.set_ylabel("Pop. Best Fitness")
ax3.legend()

baseline_errorbar_4 = ax4.errorbar(generations, baseline_means, baseline_stds, linestyle="none", marker='o', color=first_color, elinewidth=1, capsize=1, markersize=2)
addnode6_errorbar = ax4.errorbar(generations, addnode6_means, addnode6_stds, linestyle="none", marker='o', color=second_color, elinewidth=1, capsize=1, markersize=2)
addnode9_errorbar = ax4.errorbar(generations, addnode9_means, addnode9_stds, linestyle="none", marker='o', color=third_color, elinewidth=1, capsize=1, markersize=2)
addnode6_errorbar[-1][0].set_linestyle('--')
addnode9_errorbar[-1][0].set_linestyle('--')
ax4.fill_between(generations, baseline_means + baseline_stds, baseline_means - baseline_stds, color=first_color, hatch=first_hatch, alpha=first_alpha, label="Node addition 3% (BL)")
ax4.fill_between(generations, addnode6_means + addnode6_stds, addnode6_means - addnode6_stds, color=second_color, alpha=second_alpha, hatch=second_hatch, label="Node addition 6%")
ax4.fill_between(generations, addnode9_means + addnode9_stds, addnode9_means - addnode9_stds, color=third_color, alpha=third_alpha, hatch=third_hatch, label="Node addition 9%")
ax4.set_xlabel("Generation")
ax4.set_ylabel("Pop. Best Fitness")
ax4.legend()

baseline_errorbar_5 = ax5.errorbar(generations, baseline_means, baseline_stds, linestyle="none", marker='o', color=first_color, elinewidth=1, capsize=1, markersize=2)
wm40_errorbar = ax5.errorbar(generations, wm40_means, wm40_stds, linestyle="none", marker='o', color=second_color, elinewidth=1, capsize=1, markersize=2)
wm60_errorbar = ax5.errorbar(generations, wm60_means, wm60_stds, linestyle="none", marker='o', color=third_color, elinewidth=1, capsize=1, markersize=2)
wm40_errorbar[-1][0].set_linestyle('--')
wm60_errorbar[-1][0].set_linestyle('--')
ax5.fill_between(generations, baseline_means + baseline_stds, baseline_means - baseline_stds, color=first_color, hatch=first_hatch, alpha=first_alpha, label="Weight mutation 80% (BL)")
ax5.fill_between(generations, wm40_means + wm40_stds, wm40_means - wm40_stds, color=second_color, alpha=second_alpha, hatch=second_hatch, label="Weight mutation 40%")
ax5.fill_between(generations, wm60_means + wm60_stds, wm60_means - wm60_stds, color=third_color, alpha=third_alpha, hatch=third_hatch, label="Weight mutation 60%")
ax5.set_xlabel("Generation")
ax5.set_ylabel("Pop. Best Fitness")
ax5.legend()

# fig.text(0.04, 0.5, 'common Y', va='center', rotation='vertical')
# plt.ylabel("Population Best Fitness")

fig.tight_layout()
plt.subplots_adjust(wspace=0)
plt.subplots_adjust(hspace=.0)
fig.savefig("stacked_sensitivity_plots.png")
plt.show()

