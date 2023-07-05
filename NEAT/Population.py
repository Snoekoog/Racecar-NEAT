from .Genome import Genome
from .Species import Species
from .Connection import Connection
from .Innovation_History import Innovation_History
import random
from itertools import count
from .config import POPULATION_CONFIG
from copy import deepcopy
import pickle


class Population:

    def __init__(self, population_size: int, max_generations: int, fitness_function: callable, input_space: int, output_space: int, inject_genomes: list[Genome]= None ,do_species_target: bool = False, verbose: bool = True):

        # NEAT data
        self.genomes = []
        self.species = []
        self.generation_number = 0
        self.best_genome = None
        self.old_best_genome = None
        self.next_genome_id = count(0)
        self.next_species_id = count(0)
        self.innovation_history = Innovation_History()
        self.compatability_multiplier = 1
        self.finished = False
        self.inject_genomes = inject_genomes

        # Settings
        self.population_size = population_size
        self.max_generations = max_generations
        self.fitness_function = fitness_function
        self.input_space = input_space
        self.output_space = output_space
        self.verbose = verbose

        # For other versions of NEAT
        # self.best_species = None

    def run(self):

        while self.generation_number < self.max_generations and not self.finished:
            self.epoch()
            if self.verbose:
                self.printer()

    def epoch(self):

        self.allocate_children()
        self.kill_stale_species()
        self.truncate_and_reproduce()
        self.fill_population()
        self.update_fitnesses()
        self.speciate()
        self.adjust_compatibility_threshold()
        self.update_species()
        self.generation_number += 1

    def speciate(self):

        for genome in self.genomes:
            has_species = False
            for species in self.species:
                if species.compatible(genome, self.compatability_multiplier):
                    species.add_genome(genome)
                    has_species = True
                    break
            if not has_species:
                species_id = next(self.next_species_id)
                self.species.append(Species(genome, species_id))

        self.species[:] = filter(lambda s: len(s.genomes) > 0, self.species)

    def kill_stale_species(self):

        new_species = []
        for species in self.species:
            if (species.staleness < POPULATION_CONFIG.STALENESS_THRESHOLD or self.best_genome in species.genomes) and species.allocated_children > 0:
                new_species.append(species)
            else:
                if self.best_genome in species.genomes:
                    print("GOOD SPECIES ELIMINATED")

        self.species[:] = new_species

    def allocate_children(self):

        aggregated_fitness = sum(species.average_fitness for species in self.species)

        for species in self.species:
            species.allocated_children = int(round(self.population_size * species.average_fitness / aggregated_fitness))

    def truncate_and_reproduce(self):

        for species in self.species:

            survivor_size = max(1, int(round(POPULATION_CONFIG.SURVIVAL_RATE * len(species.genomes))))
            survivor_pool = species.genomes[:survivor_size]
            species.genomes[:] = []

            if POPULATION_CONFIG.ELITISM and len(survivor_pool) > POPULATION_CONFIG.MIN_ELITISM_SIZE:
                species.add_genome(species.best_genome)

            while len(species.genomes) < species.allocated_children:

                tournament_size = min(len(survivor_pool), POPULATION_CONFIG.TOURNAMENT_SIZE)

                parent_1 = self.tournament_selection(survivor_pool, tournament_size)
                parent_2 = self.tournament_selection(survivor_pool, tournament_size)

                offspring = self.crossover(parent_1, parent_2, next(self.next_genome_id))
                offspring.mutate()

                species.add_genome(offspring) 
                
        self.genomes[:] = []
        for species in self.species:
            self.genomes.extend(species.genomes)
            species.genomes[:] = []
            species.age += 1

    def fill_population(self):

        if self.inject_genomes and self.generation_number == 0 and all([isinstance(genome, Genome) for genome in self.inject_genomes]):
            self.genomes.extend(self.inject_genomes)

        while len(self.genomes) < self.population_size:

            new_genome = Genome(next(self.next_genome_id), self.innovation_history, None, None, self.input_space, self.output_space)
            self.genomes.append(new_genome)

    def update_fitnesses(self):

        for genome in self.genomes:
            genome.build_network()
            genome.age += 1

        self.finished = self.fitness_function(self.genomes)

        self.genomes.sort(reverse=True, key=lambda x: x.fitness)
        self.old_best_genome = self.best_genome
        if self.best_genome == None or self.genomes[0].fitness > self.best_genome.fitness:
            self.best_genome = self.genomes[0]

    def update_species(self):
        
        for species in self.species:
            species.genomes.sort(reverse=True, key=lambda x: x.fitness)
            species.old_best_genome = species.best_genome
            species.best_genome = species.genomes[0]

            if species.best_genome.fitness > species.old_best_genome.fitness:
                species.staleness = 0
            else:
                species.staleness += 1

            aggregated_fitness = 0
            for genome in species.genomes:
                genome_fitness = genome.fitness
                aggregated_fitness += genome_fitness

                if species.age < POPULATION_CONFIG.YOUNG_AGE_THRESHOLD:
                    genome_fitness *= POPULATION_CONFIG.YOUNG_AGE_BONUS
                elif species.age > POPULATION_CONFIG.OLD_AGE_THRESHOLD:
                    genome_fitness *= POPULATION_CONFIG.OLD_AGE_PENALTY
                genome.adjusted_fitness = genome_fitness / len(species.genomes)

            species.average_fitness = aggregated_fitness / len(species.genomes)


    def tournament_selection(self, pool, tournament_size):

        champion = None

        for _ in range(tournament_size):
            genome = random.choice(pool)
            if champion == None or genome.fitness > champion.fitness:
                champion = genome
        return champion

    def random_selection(self, genomes):
        return random.choice(genomes)
    
    def crossover(self, parent_1, parent_2, offspring_ID):

        n_1 = len(parent_1.connections)
        n_2 = len(parent_2.connections)

        better = sorted([parent_1, parent_2], reverse=True, key=lambda x: (x.fitness, 1 / len(x.connections)))[0]

        offspring_nodes = []
        offspring_connections = []

        i_1 = i_2 = 0
        node_ids = set()

        while i_1 < n_1 or i_2 < n_2:
            parent_1_gene = parent_1.connections[i_1] if i_1 < n_1 else None
            parent_2_gene = parent_2.connections[i_2] if i_2 < n_2 else None
            selected_gene = None
            if parent_1_gene and parent_2_gene:
                if parent_1_gene.innovation_number == parent_2_gene.innovation_number:
                    idx = random.randint(0,1)
                    selected_gene = (parent_1_gene,parent_2_gene)[idx]
                    selected_genome = (parent_1,parent_2)[idx]
                    i_1 += 1
                    i_2 += 1
                elif parent_2_gene.innovation_number < parent_1_gene.innovation_number:
                    if better == parent_2:
                        selected_gene = parent_2.connections[i_2]
                        selected_genome = parent_2
                    i_2 += 1
                elif parent_1_gene.innovation_number < parent_2_gene.innovation_number:
                    if better == parent_1:
                        selected_gene = parent_1_gene
                        selected_genome = parent_1
                    i_1 += 1
            elif parent_1_gene == None and parent_2_gene:
                if better == parent_2:
                    selected_gene = parent_2.connections[i_2]
                    selected_genome = parent_2
                i_2 += 1
            elif parent_1_gene and parent_2_gene == None:
                if better == parent_1:
                    selected_gene = parent_1_gene
                    selected_genome = parent_1
                i_1 += 1

            if selected_gene and len(offspring_connections) and offspring_connections[len(offspring_connections)-1].innovation_number == selected_gene.innovation_number:
                selected_gene = None

            if selected_gene != None:
                offspring_connections.append(deepcopy(selected_gene))
                if not selected_gene.origin_node_ID in node_ids:
                    node = selected_genome.get_node_by_id(selected_gene.origin_node_ID)
                    if node != None:
                        offspring_nodes.append(deepcopy(node))
                        node_ids.add(selected_gene.origin_node_ID)
                if not selected_gene.target_node_ID in node_ids:
                    node = selected_genome.get_node_by_id(selected_gene.target_node_ID)
                    if node != None:
                        offspring_nodes.append(deepcopy(node))
                        node_ids.add(selected_gene.target_node_ID)

        for node in parent_1.get_zero_layer_nodes():
            if not node.ID in node_ids:
                offspring_nodes.append(deepcopy(node))
                node_ids.add(node.ID)

        if all([not l.enabled for l in offspring_connections]):
            random.choice(offspring_connections).enabled = True

        innovation_db = parent_1.innovation_history
        n_inputs = parent_1.input_space
        n_outputs = parent_1.output_space
        offspring = Genome(offspring_ID, innovation_db, offspring_nodes, offspring_connections, n_inputs, n_outputs)

        return offspring

    def adjust_compatibility_threshold(self):
        if len(self.species) < POPULATION_CONFIG.TARGET_SPECIES_SIZE:
            self.compatability_multiplier *= 0.95
        elif len(self.species) > POPULATION_CONFIG.TARGET_SPECIES_SIZE:
            self.compatability_multiplier *= 1.05
    
    def printer(self):
        print("-"*140)
        print(f'{"Generation: " + str(self.generation_number):^140}')
        print(f'{"Species ID:":<20}' + "|" +  ' '.join(f'{species.id:<10}' + "|" for species in self.species))
        print(f'{"Species Size:":<20}' + "|" +  ' '.join(f'{len(species.genomes):<10}' + "|" for species in self.species))
        print(f'{"Species avg.fit.:":<20}' + "|" +  ' '.join(f'{round(species.average_fitness, 2):<10}' + "|" for species in self.species))
        print(f'{"Species best.fit.:":<20}' + "|" +  ' '.join(f'{round(species.best_genome.fitness, 2):<10}' + "|" for species in self.species))
        print(f'{"Best Genome layers:":<20}' + "|" +  ' '.join(f'{species.best_genome.layers:<10}' + "|" for species in self.species))
        print(f'{"Best Genome Nodes:":<20}' + "|" +  ' '.join(f'{len(species.best_genome.nodes):<10}' + "|" for species in self.species))
        print("-"*140)
        print("Other Statistics:" + "  |  " + "Compatability Factor = " + str(self.compatability_multiplier) + "  |  " + "Finished = " + str(self.finished))
        pass