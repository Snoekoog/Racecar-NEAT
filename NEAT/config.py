
# Parameters related to connections
class CONNECTION_CONFIG:
    MUTATE_RESET = 0.1              # Chance of resetting weight
    MAX_WEIGHT = 10.0               # Max allowable connection weight
    MIN_WEIGHT = -10.0              # Min allowable connection weight
    STD_DEV_WEIGHT = 2.0            # Standard deviation of normal dist. when resetting / setting a weight
    STD_DEV_WEIGHT_VAR = 1.5        # Standard deviation of normal dist. when adjusting a weight

# Parameters related to the population / basic NEAT
class POPULATION_CONFIG:
    STALENESS_THRESHOLD = 20        # After how many 'stale' generations a species is removed
    SURVIVAL_RATE = 0.5             # Fraction of genomes in species used as parents for crossover
    YOUNG_AGE_THRESHOLD = 10        # (UNUSED) Threshold for age of young genomes in weight adjustment
    YOUNG_AGE_BONUS = 1.3           # (UNUSED) Bonus for your genomes
    OLD_AGE_THRESHOLD = 50          # (UNUSED) Threshold for age of old genomes in weight adjustment
    OLD_AGE_PENALTY = 0.7           # (UNUSED) Penalty for old genomes
    TARGET_SPECIES_SIZE = 6         # Target number of species
    TOURNAMENT_SIZE = 3             # Tournament size
    ELITISM = True                  # Elimitism enabled or not
    MIN_ELITISM_SIZE = 0            # Minimum size of species needed for elitism

# Parameters related to the species
class SPECIES_CONFIG:
    COMPATABILITY_THRESHOLD = 3.0   # Compatability threshold for speciation
    DISJOINT_COEFFICIENT = 1.0      # Coefficient for disjoint factor
    EXCESS_COEFFICIENT = 1.0        # Coefficient for excess factor
    WEIGHT_COEFFICIENT = 0.4        # Coefficient for weight difference factor

# Parameters related to genomes
class GENOME_CONFIG:
    MUTATION_WEIGHT = 0.8           # Chance of mutating connection weight
    MUTATION_ACTIVATION = 0.9       # Chance of mutating sigmoid slope
    MUTATION_ADD_NODE = 0.03        # Chance of adding a node to the network
    MUTATION_ADD_CONNECTION = 0.3   # Chance of adding a connection to the network
    MUTATION_ADD_RECURRENT = 0.05   # Chance of adding a recurrent connection
    MUTATION_ACTIVATION_VAR = 1.0   # Standard deviation of sigmoid slope change
    MUTATION_ACTIVATION_PERTURBATION = 0.1 
    MUTATION_DESELECTION = 0.3      # Chance of removing a connection from the network
    FIND_LINK_TRIES = 5             # Attempts to find a connection between nodes
    FIND_UNLINKED_NODES_TRIES = 5   # Attempts to find two unconnected nodes

# Parameters related to nodes
class NODE_CONFIG:
    STANDARD_ACTIVATION_RESPONSE = 1/4.924273
    STANDARD_ACTIVATION_TYPE = "ScaledSigmoid"