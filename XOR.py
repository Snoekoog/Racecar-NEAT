import numpy as np
from racegame.config import windowHeight, windowWidth
from NEAT.Population import *

class Game:

    def __init__(self, number_agents, max_generations):
        
        self.number_agents = number_agents
        self.max_generations = max_generations
        self.population = Population(self.number_agents, self.max_generations, self.determine_fitness, 2, 1)
        self.finished = False
        self.EPSILON = 1e-100
        self.input_data = np.array( [(0,0), (0,1), (1,0), (1,1)] , dtype=float)
        self.output_data = np.array( [(-1,), (1,), (1,), (-1,)] , dtype=float)
        self.found_in = 50
        self.did_finish = False
        self.best_fitnesses = []
        self.best_genome = None
        self.best_genome_fitness = 0
        # self.input_data = np.linspace(-10, 10, 100)
        # self.output_data = self.input_data**2
        # self.input_data = self.input_data.reshape(len(self.input_data), 1)
        # self.output_data = self.output_data.reshape(len(self.input_data), 1)
        self.population.run()
        pass

    def determine_fitness(self, genomes):

        avg_fitness = 0
        avg_size = 0
        best_fitness = 0
        finished = False
        for genome in genomes:

            mse = 0.0
            for (input, target) in zip(self.input_data, self.output_data):

                output = genome.feed_forward3(input)
                # print(output)
                err = target - output
                # print(err)
                err[abs(err) < self.EPSILON] = 0
                mse += (err ** 2).mean()

            # print("MSE: " + str(mse))
            rmse = np.sqrt(mse / len(self.input_data))
            # print("RMSE: " + str(rmse))
            score = 1/(1+rmse) # fitness score
            # print("score: " + str(score))
            genome.fitness = score
            avg_fitness += score
            avg_size += len(genome.nodes)
            if score > best_fitness:
                best_fitness = score
            if score > self.best_genome_fitness:
                self.best_genome_fitness = best_fitness
                self.best_genome = genome
        finished = best_fitness > 0.99
        if finished and self.did_finish == False:
            self.did_finish = True
            self.found_in = self.population.generation_number
        print('Gen ' + str(self.population.generation_number) + ': Best score of generation: ' + str(best_fitness) + " and finished " + str(finished))
        if len(self.best_fitnesses) > 0 and self.best_fitnesses[-1] > best_fitness:
            print("DEGRADING")
        self.best_fitnesses.append(best_fitness)
        # print([node.type + " node " + str(node.ID) + " in layer " + str(node.layer) for node in genome.nodes])

        return finished

solve_xor = Game(120, 50)

# results = []
# for i in range(50):
#     print(i)
#     solve_xor = Game(120, 50)
#     results.append(solve_xor.found_in)

# np_results = np.array(results)
# mean = np.mean(np_results)
# print(mean)
