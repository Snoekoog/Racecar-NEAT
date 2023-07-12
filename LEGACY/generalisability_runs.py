import math as m
import numpy as np
import matplotlib.pyplot as plt
import json

with open("./NEAT_RUN_STATS/silverstone-base-run-1.json", 'r') as f:
    run0 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-transfer-redbullring.json", 'r') as f:
    run1 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-transfer-spa.json", 'r') as f:
    run2 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-transfer-yasmarina.json", 'r') as f:
    run3 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-transfer-monza.json", 'r') as f:
    run4 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-transfer-zandvoort.json", 'r') as f:
    run5 = json.load(f)

with open("./NEAT_RUN_STATS/silverstone-transfer-hungaroring.json", 'r') as f:
    run6 = json.load(f)

fig, ax = plt.subplots()

generations = run0['generations'][:20]
run0_popmax = np.array(run0['best_fitness'][:20])
run1_popmax = np.array(run1['best_fitness'])
run2_popmax = np.array(run2['best_fitness'])
run3_popmax = np.array(run3['best_fitness'])
run4_popmax = np.array(run4['best_fitness'])
run5_popmax = np.array(run5['best_fitness'])
run6_popmax = np.array(run6['best_fitness'])

ax.plot(generations, run0_popmax, label="Silverstone evolution")
ax.plot(generations, run1_popmax, label="→ Redbull Ring")
ax.plot(generations, run2_popmax, label="→ Spa-Franchorchamps")
ax.plot(generations, run3_popmax, label="→ Yas Marina")
ax.plot(generations, run4_popmax, label="→ Monza")
ax.plot(generations, run5_popmax, label="→ Zandvoort")
ax.plot(generations, run6_popmax, label="→ Hungaroring")

ax.set_ylabel("Population Best Fitness")
ax.set_xlabel("Generation")

fig.set_size_inches(8, 4.0)
fig.tight_layout()
ax.set_xticks([0, 5, 10, 15, 20])
plt.legend(ncol=2, loc=2, fontsize=9.2)
plt.show()