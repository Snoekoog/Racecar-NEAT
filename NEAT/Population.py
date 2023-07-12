from .Genome import Genome
from .Species import Species
from .Connection import Connection
from .Innovation_History import Innovation_History
import random
from itertools import count
from .config import POPULATION_CONFIG
from copy import deepcopy
import json
import os
import pickle
import time
import numpy as np
import matplotlib.pyplot as plt


class Population:

    def __init__(self, population_size: int, max_generations: int, fitness_function: callable, input_space: int, output_space: int, inject_genomes: list[Genome]= None ,do_species_target: bool = False, verbose: bool = True, do_graph: bool = True, save_stats: bool = True):

        # NEAT data
        self.genomes                    = []                                # Genomes in population
        self.species                    = []                                # Species in population
        self.generation_number          = 0                                 # What generation we're in
        self.best_genome                = None                              # Best genome found in population
        self.old_best_genome            = None                              # 1-old history of best genome
        self.next_genome_id             = count(0)                          # Counter for next genome id
        self.next_species_id            = count(0)                          # Counter for next species id
        self.innovation_history         = Innovation_History()              # Innovation history instance
        self.compatability_multiplier   = 1                                 # Multiplier for compatability threshold (to control nr of species)
        self.finished                   = False                             # Is finished? (has reached goal?)
        self.inject_genomes             = inject_genomes                    # Genomes to inject into population

        # Settings
        self.population_size            = population_size                   # Size of population
        self.max_generations            = max_generations                   # Max number of generations
        self.fitness_function           = fitness_function                  # Fitness function (CALLABLE with input of list of genomes)
        self.input_space                = input_space                       # Number of inputs
        self.output_space               = output_space                      # Number of outputs
        self.verbose                    = verbose                           # Spam to console the statistics?
        self.do_graph                   = do_graph                          # Generate graphs afterwards?
        self.save_stats                 = save_stats                        # Save stats afterwards?
        self.identifier                 = time.strftime("%Y%m%d-%H%M%S")    # Identifier for this run (for saving stats later)
        self.statistics = {
            "total_gens": 0,
            "generations": [],
            "best_fitness": [],
            "species": []
        }

    # Run the algorithm
    def run(self):

        # While we still have generations to go
        while self.generation_number < self.max_generations and not self.finished:

            # Do a full epoch
            self.epoch()

            # If verbose, print that sh*t to console!
            if self.verbose:
                self.printer()

            # If we want to either graph or save the statistics
            if self.do_graph or self.save_stats:

                # Loop through species
                for species in self.species:
                    
                    # If we do not have a container for this species yet, create one (empty list)
                    while len(self.statistics['species']) <= species.id:
                        self.statistics['species'].append([])

                    # Create list of desired data
                    species_data = [self.generation_number, len(species.genomes), species.best_genome.fitness]

                    # Add to the 'container' for this species
                    self.statistics['species'][species.id].append(species_data)

                # Add general data
                self.statistics['generations'].append(self.generation_number)
                self.statistics['best_fitness'].append(self.best_genome.fitness)
                self.statistics['total_gens'] = self.generation_number

        # After evolution, if we want graphs, make them
        if self.do_graph:
            self.graph()

        # Similarly for saving stats
        if self.save_stats:
            self.save_statistics()

    # One epoch (generation)
    def epoch(self):

        self.allocate_children()                # Allocate children to species
        self.kill_stale_species()               # Kill stale (non performing) species
        self.truncate_and_reproduce()           # Truncate best few, and reproduce for offspring
        self.fill_population()                  # If we have not filled the population yet, make extra genomes
        self.update_fitnesses()                 # Run fitness test on all genomes
        self.speciate()                         # Speciate (put genomes into species)
        self.adjust_compatibility_threshold()   # Adjust threshold to make sure we get to the desired nr of species
        self.update_species()                   # Update the species
        self.generation_number += 1             # Next generation!

    # Allocate children based on species performance
    def allocate_children(self):

        # Total combined average fitness of all species
        aggregated_fitness = sum(species.average_fitness for species in self.species)

        # Allocate offspring based on their contribution
        for species in self.species:
            species.allocated_children = int(round(self.population_size * species.average_fitness / aggregated_fitness))

    # Kill stale species
    def kill_stale_species(self):

        # First, create empty list of species
        new_species = []
        
        # Loop through all species
        for species in self.species:

            # If they do not exceed staleness AND are allocated at least 1 offspring, add them to the next generation species
            if (species.staleness < POPULATION_CONFIG.STALENESS_THRESHOLD or self.best_genome in species.genomes) and species.allocated_children > 0:
                new_species.append(species)

            # Otherwise we discard them
            else:

                # But do notify if we lose our best genome because of it
                if self.best_genome in species.genomes:
                    print("GOOD SPECIES ELIMINATED")

        # Update new species
        self.species[:] = new_species

    # Truncation and reproduction
    def truncate_and_reproduce(self):

        # Loop through species
        for species in self.species:

            # Number of genomes used as offspring
            survivor_size = max(1, int(round(POPULATION_CONFIG.SURVIVAL_RATE * len(species.genomes))))

            # Truncate from total list of genomes
            survivor_pool = species.genomes[:survivor_size]

            # Reset species genomes to empty
            species.genomes[:] = []

            # Due to elitism, add best performing genome to next generation automatically
            if POPULATION_CONFIG.ELITISM and len(survivor_pool) > POPULATION_CONFIG.MIN_ELITISM_SIZE:
                species.add_genome(species.best_genome)

            # If we have not met the required number of species members yet
            while len(species.genomes) < species.allocated_children:

                # Calculate tournament size
                tournament_size = min(len(survivor_pool), POPULATION_CONFIG.TOURNAMENT_SIZE)

                # Select two parents through tournament selection
                parent_1 = self.tournament_selection(survivor_pool, tournament_size)
                parent_2 = self.tournament_selection(survivor_pool, tournament_size)

                # Crossover between the two
                offspring = self.crossover(parent_1, parent_2, next(self.next_genome_id))

                # Mutate offspring
                offspring.mutate()

                # Add offspring to species
                species.add_genome(offspring) 
                
        # Reset population genomes
        self.genomes[:] = []

        # For all species, add its genomes to the total population and add one to its age
        for species in self.species:
            self.genomes.extend(species.genomes)
            species.genomes[:] = []
            species.age += 1

    # Fill the population if it does not have enough genomes
    def fill_population(self):

        # Here, we add the injected genomes but only if it's the first generation.
        if self.inject_genomes and self.generation_number == 0 and all([isinstance(genome, Genome) for genome in self.inject_genomes]):
            self.genomes.extend(self.inject_genomes)

        # Add genomes while we have not met the required population size yet
        while len(self.genomes) < self.population_size:

            new_genome = Genome(next(self.next_genome_id), self.innovation_history, None, None, self.input_space, self.output_space)
            self.genomes.append(new_genome)

    # Update fitnesses of genomes
    def update_fitnesses(self):

        # First, build their networks
        for genome in self.genomes:
            genome.build_network()
            genome.age += 1

        # Fitness function determines whether it is finished or not
        self.finished = self.fitness_function(self.genomes)

        # Sort genomes by fitness
        self.genomes.sort(reverse=True, key=lambda x: x.fitness)

        # Set old best genome to current best genome
        self.old_best_genome = self.best_genome

        # If we have a better genome, update best genome
        if self.best_genome == None or self.genomes[0].fitness > self.best_genome.fitness:
            self.best_genome = self.genomes[0]

    # Speciation (moving genomes into species)
    def speciate(self):

        # Loop through genomes
        for genome in self.genomes:

            # Boolean to indicate if a species has been found for it
            has_species = False

            # Loop through species
            for species in self.species:

                # If it is compatible, add it to the species genomes list
                if species.compatible(genome, self.compatability_multiplier):
                    species.add_genome(genome)
                    has_species = True
                    break
            # If no species has been found, create a new one for it
            if not has_species:
                species_id = next(self.next_species_id)
                self.species.append(Species(genome, species_id))

        # Update species but leave species out with no genomes
        self.species[:] = filter(lambda s: len(s.genomes) > 0, self.species)

    # Adjust compatability threshold such that we try to match the desired number of species
    def adjust_compatibility_threshold(self):
        if len(self.species) < POPULATION_CONFIG.TARGET_SPECIES_SIZE:
            self.compatability_multiplier *= 0.95
        elif len(self.species) > POPULATION_CONFIG.TARGET_SPECIES_SIZE:
            self.compatability_multiplier *= 1.05

    # Update all the species from this generation
    def update_species(self):
        
        # Loop through species
        for species in self.species:

            # Sort its genomes
            species.genomes.sort(reverse=True, key=lambda x: x.fitness)

            # Update the (old) best genome
            species.old_best_genome = species.best_genome
            species.best_genome = species.genomes[0]

            # If we see a fitness improvement, we reset staleness. Otherwise we add one to it.
            if species.best_genome.fitness > species.old_best_genome.fitness:
                species.staleness = 0
            else:
                species.staleness += 1

            # Accumulator for total fitness of species
            aggregated_fitness = 0

            # Loop through genomes in species
            for genome in species.genomes:

                # Add the fitness of the genome to the accumulator
                genome_fitness = genome.fitness
                aggregated_fitness += genome_fitness

                # # (UNUSED) for fitness sharing
                # if species.age < POPULATION_CONFIG.YOUNG_AGE_THRESHOLD:
                #     genome_fitness *= POPULATION_CONFIG.YOUNG_AGE_BONUS
                # elif species.age > POPULATION_CONFIG.OLD_AGE_THRESHOLD:
                #     genome_fitness *= POPULATION_CONFIG.OLD_AGE_PENALTY
                # genome.adjusted_fitness = genome_fitness / len(species.genomes)

            # Compute average fitness of species
            species.average_fitness = aggregated_fitness / len(species.genomes)

    # Tournament selection
    def tournament_selection(self, pool, tournament_size):

        # Winner of tournament
        champion = None

        # Keep finding contestants
        for _ in range(tournament_size):

            # Pick random contestant
            genome = random.choice(pool)

            # If it beats the champion it becomes the new champion
            if champion == None or genome.fitness > champion.fitness:
                champion = genome

        # Return it
        return champion

    # Alternative for tournament selection
    def random_selection(self, genomes):
        return random.choice(genomes)
    
    # Crossover between two parents
    def crossover(self, parent_1: Genome, parent_2: Genome, offspring_ID: int):

        # Number of connections of each parent
        n_1 = len(parent_1.connections)
        n_2 = len(parent_2.connections)

        # Select better parrent according to fitness and fewest connections
        better = sorted([parent_1, parent_2], reverse=True, key=lambda x: (x.fitness, 1 / len(x.connections)))[0]

        # Lists for nodes and connections of offspring
        offspring_nodes = []
        offspring_connections = []

        # Idx's and set for node ids
        i_1 = i_2 = 0
        node_ids = set()

        while i_1 < n_1 or i_2 < n_2:
            
            # Select connections
            parent_1_connection = parent_1.connections[i_1] if i_1 < n_1 else None
            parent_2_connection = parent_2.connections[i_2] if i_2 < n_2 else None
            selected_connection = None

            # If both connections exist
            if parent_1_connection and parent_2_connection:

                # And innovation numbers are equal
                if parent_1_connection.innovation_number == parent_2_connection.innovation_number:

                    # Select connection at random
                    idx = random.randint(0,1)
                    selected_connection = (parent_1_connection,parent_2_connection)[idx]
                    selected_genome = (parent_1,parent_2)[idx]
                    i_1 += 1
                    i_2 += 1

                # If parent 2's connection has an earlier innovation
                elif parent_2_connection.innovation_number < parent_1_connection.innovation_number:
                    if better == parent_2:
                        selected_connection = parent_2.connections[i_2]
                        selected_genome = parent_2
                    i_2 += 1

                # If parent 1's connection has an earlier innovation
                elif parent_1_connection.innovation_number < parent_2_connection.innovation_number:
                    if better == parent_1:
                        selected_connection = parent_1_connection
                        selected_genome = parent_1
                    i_1 += 1

            # If only parent 2 has a valid connection
            elif parent_1_connection == None and parent_2_connection:
                if better == parent_2:
                    selected_connection = parent_2.connections[i_2]
                    selected_genome = parent_2
                i_2 += 1

            # If only parent 1 has a valid connection
            elif parent_1_connection and parent_2_connection == None:
                if better == parent_1:
                    selected_connection = parent_1_connection
                    selected_genome = parent_1
                i_1 += 1

            if selected_connection and len(offspring_connections) and offspring_connections[len(offspring_connections)-1].innovation_number == selected_connection.innovation_number:
                selected_connection = None

            # If a connection was selected
            if selected_connection != None:

                # Copy the connection from the parent
                offspring_connections.append(deepcopy(selected_connection))

                # If the origin node does not exist in the offspring nodes
                if not selected_connection.origin_node_ID in node_ids:

                    # Check if parent has it
                    node = selected_genome.get_node_by_id(selected_connection.origin_node_ID)

                    # If so
                    if node != None:

                        # Add it to the offspring's nodes
                        offspring_nodes.append(deepcopy(node))
                        node_ids.add(selected_connection.origin_node_ID)

                # If the target node does not exist in the offspring nodes
                if not selected_connection.target_node_ID in node_ids:

                    # Check if parent has it
                    node = selected_genome.get_node_by_id(selected_connection.target_node_ID)

                    # If so
                    if node != None:

                        # Add it to the offspring's nodes
                        offspring_nodes.append(deepcopy(node))
                        node_ids.add(selected_connection.target_node_ID)

        # For all input and output nodes
        for node in parent_1.get_edge_nodes():
            
            # If offspring does not already have it
            if not node.ID in node_ids:

                # Add it to the offspring's nodes
                offspring_nodes.append(deepcopy(node))
                node_ids.add(node.ID)

        # If literally all connections are disabled
        if all([not l.enabled for l in offspring_connections]):

            # Just enable one at random
            random.choice(offspring_connections).enabled = True

        # Carry over properties of parent
        innovation_db = parent_1.innovation_history
        n_inputs = parent_1.input_space
        n_outputs = parent_1.output_space
        offspring = Genome(offspring_ID, innovation_db, offspring_nodes, offspring_connections, n_inputs, n_outputs)

        # Return offspring
        return offspring
    
    # To print statistics to console
    def printer(self):
        print("-"*140)
        print(f'{"Generation: " + str(self.generation_number):^140}')
        print(f'{"Species ID:":<20}' + "|" +  ' '.join(f'{species.id:<10}' + "|" for species in self.species))
        print(f'{"Species age:":<20}' + "|" +  ' '.join(f'{species.age:<10}' + "|" for species in self.species))
        print(f'{"Species Size:":<20}' + "|" +  ' '.join(f'{len(species.genomes):<10}' + "|" for species in self.species))
        print(f'{"Species avg.fit.:":<20}' + "|" +  ' '.join(f'{round(species.average_fitness, 2):<10}' + "|" for species in self.species))
        print(f'{"Species best.fit.:":<20}' + "|" +  ' '.join(f'{round(species.best_genome.fitness, 2):<10}' + "|" for species in self.species))
        print(f'{"Best Genome layers:":<20}' + "|" +  ' '.join(f'{species.best_genome.layers:<10}' + "|" for species in self.species))
        print(f'{"Best Genome Nodes:":<20}' + "|" +  ' '.join(f'{len(species.best_genome.nodes):<10}' + "|" for species in self.species))
        print("-"*140)
        print("Other Statistics:" + "  |  " + "Compatibility Factor = " + str(self.compatability_multiplier) + "  |  " + "Finished = " + str(self.finished))

    # To create graphs at the end of the evolution
    def graph(self):

        # Data for each generation for each species
        data = np.zeros([self.statistics['total_gens'], len(self.statistics['species'])])

        # For all species data 'containers'
        for i in range(len(self.statistics['species'])):

            # Extract data for that species
            s_data = np.array(self.statistics['species'][i])

            # Obtain the first generation it existed, and the last generation
            first_gen = int(s_data[0, 0])
            last_gen = int(s_data[-1, 0])

            # Fill that sequence into the big matrix
            data[first_gen-1:last_gen, i] = s_data[:, 1]

        # Create plot for species and their shares of the population
        fig, ax = plt.subplots()
        ax.stackplot(np.arange(self.generation_number), data.T, alpha = 0.4)
        ax.set_xlim(0, self.statistics['total_gens']-1)
        ax.set_xlabel("Generation")
        ax.set_ylabel("Genomes")

        # Create plots for the species best fitness of each generation
        fig2, ax2 = plt.subplots()
        for i in range(len(self.statistics['species'])):
            species_data = np.array(self.statistics['species'][i])
            ax2.plot(species_data[:,0], species_data[:,2])
        ax2.set_xlabel("Generation")
        ax2.set_ylabel("Species Best Fitness")

        # Create plots for the population best fitness of each generation
        fig3, ax3 = plt.subplots()
        ax3.plot(self.statistics['generations'], self.statistics['best_fitness'], color='black')
        ax3.set_xlabel("Generation")
        ax3.set_ylabel("Population Best Fitness")

        plt.show()

    # Save statistics after the run
    def save_statistics(self):

        # If stats folder does not exist, create it
        if not os.path.exists("NEAT_RUN_STATS"):
            os.makedirs("NEAT_RUN_STATS")

        # Save it to a json file
        with open("./NEAT_RUN_STATS/" + self.identifier + ".json", 'w') as f:
            json.dump(self.statistics, f, indent=2) 