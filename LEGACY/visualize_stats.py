import matplotlib.pyplot as plt
import numpy as np
import json

with open("./NEAT_RUN_STATS/silverstone-base.json", 'r') as f:
    statistics = json.load(f)

data = np.zeros([statistics['total_gens'], len(statistics['species'])])
# print(self.statistics)
for i in range(len(statistics['species'])):
    s_data = np.array(statistics['species'][i])
    first_gen = int(s_data[0, 0])
    last_gen = int(s_data[-1, 0])
    data[first_gen-1:last_gen, i] = s_data[:, 1]

fig, (ax, ax2, ax3) = plt.subplots(3, 1, sharex=True)

ax.plot(statistics['generations'], statistics['best_fitness'], color='black')
# ax.set_xlabel("Generation")
ax.set_ylabel("Population Best Fitness")
plt.setp(ax.get_xticklabels(), visible=False)
# ax3.annotate('Agent goes through first corner',
#             xy=(1, statistics['best_fitness'][0]), xycoords='data')
# fig3.set_size_inches(14, 3.5)
# fig3.tight_layout()
ax.annotate(
    'Agent goes through first corner',
    xy=(1, statistics['best_fitness'][0]), xycoords='data',
    xytext=(-15, 50), textcoords='offset points',
    arrowprops=dict(arrowstyle="->",
                    connectionstyle="arc,angleA=0,armA=50,rad=10"))
ax.annotate(
    'Agent passes all corners till hairpin at 3/4;\nhidden node added to network',
    xy=(10, statistics['best_fitness'][9]), xycoords='data',
    xytext=(-180, 45), textcoords='offset points',
    arrowprops=dict(arrowstyle="->",
                    connectionstyle="arc,angleA=0,armA=50,rad=10"))

ax.annotate(
    'Agent passes hairpin but crashes at last corner',
    xy=(15, statistics['best_fitness'][14]), xycoords='data',
    xytext=(-220, 70), textcoords='offset points',
    arrowprops=dict(arrowstyle="->",
                    connectionstyle="arc,angleA=0,armA=50,rad=10"))

ax.annotate(
    'Agent passes last hairpain, finishes first lap and gets to 1.5\nlaps before being cut off by the time limit',
    xy=(21, statistics['best_fitness'][20]), xycoords='data',
    xytext=(-240, 60), textcoords='offset points',
    arrowprops=dict(arrowstyle="->",
                    connectionstyle="arc,angleA=0,armA=50,rad=10"))

ax.annotate(
    'Faster agent appears through mutation;\ncut off by time limit',
    xy=(24, statistics['best_fitness'][23]), xycoords='data',
    xytext=(-50, -90), textcoords='offset points',
    arrowprops=dict(arrowstyle="->",
                    connectionstyle="arc,angleA=0,armA=50,rad=10"))

ax.annotate(
    'Faster agent crashes at last corner of second lap',
    xy=(29, statistics['best_fitness'][28]), xycoords='data',
    xytext=(-130, 58), textcoords='offset points',
    arrowprops=dict(arrowstyle="->",
                    connectionstyle="arc,angleA=0,armA=50,rad=10"))

ax.annotate(
    'Agent makes it to two laps; cut off by time limit',
    xy=(31, statistics['best_fitness'][30]), xycoords='data',
    xytext=(-55, -80), textcoords='offset points',
    arrowprops=dict(arrowstyle="->",
                    connectionstyle="arc,angleA=0,armA=50,rad=10"))

ax.annotate(
    'Agent mutated to drive faster; still time-limited',
    xy=(34, statistics['best_fitness'][33]), xycoords='data',
    xytext=(30, -60), textcoords='offset points',
    arrowprops=dict(arrowstyle="->",
                    connectionstyle="arc,angleA=0,armA=50,rad=10"))

ax.annotate(
    'Agent makes it to 2.5 laps; still time-limited',
    xy=(50, statistics['best_fitness'][49]), xycoords='data',
    xytext=(-180, -50), textcoords='offset points',
    arrowprops=dict(arrowstyle="->",
                    connectionstyle="arc,angleA=0,armA=50,rad=10"))

# fig2, ax2 = plt.subplots()
for i in range(len(statistics['species'])):
    species_data = np.array(statistics['species'][i])
    ax2.plot(species_data[:,0], species_data[:,2])
# ax2.set_xlabel("Generation")
ax2.set_ylabel("Species Best Fitness")
plt.setp(ax2.get_xticklabels(), visible=False)
ax2.set_yticks([0, 1000, 2000, 3000, 4000, 5000, 6000])

ax3.stackplot(np.arange(max(statistics['generations'])), data.T, alpha = 0.4)
ax3.set_xlim(0, statistics['total_gens']-1)
ax3.set_xlabel("Generation")
ax3.set_ylabel("Genomes")

fig.set_size_inches(14, 10.4)
fig.tight_layout()
plt.subplots_adjust(wspace=0)
plt.subplots_adjust(hspace=.0)



plt.show()