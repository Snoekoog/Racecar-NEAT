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

        n_mum = len(parent_1.connections)
        n_dad = len(parent_2.connections)

        # if parent_1.fitness == parent_2.fitness:
        #     if n_mum == n_dad:
        #         better = (parent_1, parent_2)[random.randint(0,1)]
        #     elif n_mum < n_dad:
        #         better = parent_1
        #     else:
        #         better = parent_2
        # elif parent_1.fitness > parent_2.fitness:
        #     better = parent_1
        # else:
        #     better = parent_2
        better = sorted([parent_1, parent_2], reverse=True, key=lambda x: (x.fitness, 1 / len(x.connections)))[0]

        baby_neurons = []   # neuron genes
        baby_links = []     # link genes

        # iterate over parent genes
        i_mum = i_dad = 0
        neuron_ids = set()
        while i_mum < n_mum or i_dad < n_dad:
            mum_gene = parent_1.connections[i_mum] if i_mum < n_mum else None
            dad_gene = parent_2.connections[i_dad] if i_dad < n_dad else None
            selected_gene = None
            if mum_gene and dad_gene:
                if mum_gene.innovation_number == dad_gene.innovation_number:
                    # same innovation number, pick gene randomly from mom or dad
                    idx = random.randint(0,1)
                    selected_gene = (mum_gene,dad_gene)[idx]
                    selected_genome = (parent_1,parent_2)[idx]
                    i_mum += 1
                    i_dad += 1
                elif dad_gene.innovation_number < mum_gene.innovation_number:
                    # dad has lower innovation number, pick dad's gene, if they are better
                    if better == parent_2:
                        selected_gene = parent_2.connections[i_dad]
                        selected_genome = parent_2
                    i_dad += 1
                elif mum_gene.innovation_number < dad_gene.innovation_number:
                    # mum has lower innovation number, pick mum's gene, if they are better
                    if better == parent_1:
                        selected_gene = mum_gene
                        selected_genome = parent_1
                    i_mum += 1
            elif mum_gene == None and dad_gene:
                # end of mum's genome, pick dad's gene, if they are better
                if better == parent_2:
                    selected_gene = parent_2.connections[i_dad]
                    selected_genome = parent_2
                i_dad += 1
            elif mum_gene and dad_gene == None:
                # end of dad's genome, pick mum's gene, if they are better
                if better == parent_1:
                    selected_gene = mum_gene
                    selected_genome = parent_1
                i_mum += 1

            # add gene only when it has not already been added
            # TODO: in which case do we need this?
            if selected_gene and len(baby_links) and baby_links[len(baby_links)-1].innovation_number == selected_gene.innovation_number:
                print('GENE HAS ALREADY BEEN ADDED')
                selected_gene = None

            if selected_gene != None:
                # inherit link
                baby_links.append(deepcopy(selected_gene))

                # inherit neurons
                if not selected_gene.origin_node_ID in neuron_ids:
                    neuron = selected_genome.get_node_by_id(selected_gene.origin_node_ID)
                    if neuron != None:
                        baby_neurons.append(deepcopy(neuron))
                        neuron_ids.add(selected_gene.origin_node_ID)
                if not selected_gene.target_node_ID in neuron_ids:
                    neuron = selected_genome.get_node_by_id(selected_gene.target_node_ID)
                    if neuron != None:
                        baby_neurons.append(deepcopy(neuron))
                        neuron_ids.add(selected_gene.target_node_ID)

            # in NEAT-Sweepers the baby neurons are created from innovations...
            # we lose activation_mutation in this case

        # add in- and output neurons if they are not connected
        for neuron in parent_1.get_zero_layer_nodes():
            if not neuron.ID in neuron_ids:
                baby_neurons.append(deepcopy(neuron))
                neuron_ids.add(neuron.ID)

        #print('\nCROSSOVER')
        if all([not l.enabled for l in baby_links]):
            # in case of same innovation id, we choose random and can end up with all links disabled
            random.choice(baby_links).enabled = True

        innovation_db = parent_1.innovation_history
        n_inputs = parent_1.input_space
        n_outputs = parent_1.output_space
        baby = Genome(offspring_ID, innovation_db, baby_neurons, baby_links, n_inputs, n_outputs)

        return baby

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