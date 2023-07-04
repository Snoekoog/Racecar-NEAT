from .config import SPECIES_CONFIG
from .Genome import Genome

class Species:

    def __init__(self, first_entry: Genome, id: int):

        self.id = id
        self.genomes = []
        self.staleness = 0
        self.best_fitness = 0
        self.average_fitness = 0
        self.best_genome = first_entry
        self.old_best_genome = first_entry
        self.old_best_genome = 0
        self.allocated_children = 0
        self.age = 0

        # TODO: remove? or representative = used in compatability
        # self.rep = first_entry
        
        self.add_genome(first_entry)

    def add_genome(self, genome: Genome):
        genome.species_ID = self.id
        self.genomes.append(genome)

    def compatible(self, genome: Genome, compatibility_multiplier: float) -> bool:

        n_match = n_disjoint = n_excess = 0
        weight_difference = 0

        g1_n_connections = len(genome.connections)
        g2_n_connections = len(self.best_genome.connections)
        g1_i = g2_i = 0

        while g1_i < g1_n_connections or g2_i < g2_n_connections:

            if g1_i == g1_n_connections:
                n_excess += 1
                g2_i += 1
                continue

            if g2_i == g2_n_connections:
                n_excess += 1
                g1_i += 1
                continue

            connection_1 = genome.connections[g1_i]
            connection_2 = self.best_genome.connections[g2_i]

            if connection_1.innovation_number == connection_2.innovation_number:
                n_match += 1
                g1_i += 1
                g2_i += 1
                weight_difference = weight_difference + abs(connection_1.weight - connection_2.weight)
                continue

            if connection_1.innovation_number < connection_2.innovation_number:
                n_disjoint += 1
                g1_i += 1
                continue

            if connection_1.innovation_number > connection_2.innovation_number:
                n_disjoint += 1
                g2_i += 1
                continue

        n_match += 1
        compatibility_score = (SPECIES_CONFIG.EXCESS_COEFFICIENT*n_excess + SPECIES_CONFIG.DISJOINT_COEFFICIENT*n_disjoint)/max(g1_n_connections, g2_n_connections) + SPECIES_CONFIG.WEIGHT_COEFFICIENT*weight_difference/n_match
        return compatibility_score <= (SPECIES_CONFIG.COMPATABILITY_THRESHOLD * compatibility_multiplier)
