from .config import SPECIES_CONFIG
from .Genome import Genome

class Species:

    def __init__(self, first_entry: Genome, id: int):

        self.id                     = id            # ID of species
        self.genomes                = []            # List of genomes in species
        self.staleness              = 0             # Staleness of species (generations of no improvement)
        self.best_fitness           = 0             # Best fitness (fitness of best genome)
        self.average_fitness        = 0             # Average fitness of species
        self.best_genome            = first_entry   # Best genome = first entry
        self.old_best_genome        = first_entry   # Best old genome is also first entry
        self.allocated_children     = 0             # Allowed offspring
        self.age                    = 0             # Age of species
        
        # First genome is automatically added
        self.add_genome(first_entry)

    # Add genome to species
    def add_genome(self, genome: Genome):

        # Set species id to own id and add to own genomes
        genome.species_ID = self.id
        self.genomes.append(genome)

    # Test if genome is compatible with this species
    def compatible(self, genome: Genome, compatibility_multiplier: float) -> bool:

        # Matching connections, disjoint connections, excess connections
        n_match = n_disjoint = n_excess = 0
        weight_difference = 0

        # Number of connections of candidate and own best genome
        g1_n_connections = len(genome.connections)
        g2_n_connections = len(self.best_genome.connections)

        # Iterators (idx's)
        g1_i = g2_i = 0

        # While we can still loop
        while g1_i < g1_n_connections or g2_i < g2_n_connections:

            # If one ran out of connections, theres excess in the other
            if g1_i == g1_n_connections:
                n_excess += 1
                g2_i += 1
                continue

            # And the other way around
            if g2_i == g2_n_connections:
                n_excess += 1
                g1_i += 1
                continue

            # Take connection from both genomes
            connection_1 = genome.connections[g1_i]
            connection_2 = self.best_genome.connections[g2_i]

            # If they match, we add to matching number and add weight difference
            if connection_1.innovation_number == connection_2.innovation_number:
                n_match += 1
                g1_i += 1
                g2_i += 1
                weight_difference = weight_difference + abs(connection_1.weight - connection_2.weight)
                continue

            # If one has earlier innovation than the other, they are disjoint
            if connection_1.innovation_number < connection_2.innovation_number:
                n_disjoint += 1
                g1_i += 1
                continue

            # Same here
            if connection_1.innovation_number > connection_2.innovation_number:
                n_disjoint += 1
                g2_i += 1
                continue

        # Make sure no division by zero
        n_match += 1

        # Compute compatability score
        compatibility_score = (SPECIES_CONFIG.EXCESS_COEFFICIENT*n_excess + SPECIES_CONFIG.DISJOINT_COEFFICIENT*n_disjoint)/max(g1_n_connections, g2_n_connections) + SPECIES_CONFIG.WEIGHT_COEFFICIENT*weight_difference/n_match

        # Return whether this falls below comp. threshold times multiplier
        return compatibility_score <= (SPECIES_CONFIG.COMPATABILITY_THRESHOLD * compatibility_multiplier)
