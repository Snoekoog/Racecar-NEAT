
class CONNECTION_CONFIG:
    MUTATE_RESET = 0.1
    MAX_WEIGHT = 10.0
    MIN_WEIGHT = -10.0
    STD_DEV_WEIGHT = 2.0
    STD_DEV_WEIGHT_VAR = 1.5

class POPULATION_CONFIG:
    STALENESS_THRESHOLD = 20
    SURVIVAL_RATE = 0.5
    YOUNG_AGE_THRESHOLD = 10
    YOUNG_AGE_BONUS = 1.3
    OLD_AGE_THRESHOLD = 50
    OLD_AGE_PENALTY = 0.7
    TARGET_SPECIES_SIZE = 6
    TOURNAMENT_SIZE = 3
    ELITISM = True
    MIN_ELITISM_SIZE = 0

class SPECIES_CONFIG:
    COMPATABILITY_THRESHOLD = 3.0
    DISJOINT_COEFFICIENT = 1.0
    EXCESS_COEFFICIENT = 1.0
    WEIGHT_COEFFICIENT = 0.4

class GENOME_CONFIG:
    MUTATION_WEIGHT = 0.8
    MUTATION_ACTIVATION = 0.9
    MUTATION_ADD_NODE = 0.03
    MUTATION_ADD_CONNECTION = 0.3
    MUTATION_ADD_RECURRENT = 0.05
    MUTATION_ACTIVATION_VAR = 1.0
    MUTATION_ACTIVATION_PERTURBATION = 0.1
    FIND_LINK_TRIES = 5
    FIND_UNLINKED_NODES_TRIES = 5

class NODE_CONFIG:
    STANDARD_ACTIVATION_RESPONSE = 1/4.924273
    STANDARD_ACTIVATION_TYPE = "ScaledSigmoid"