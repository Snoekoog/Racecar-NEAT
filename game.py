import numpy as np
import pyglet
from pyglet.gl import *
from racegame.car import Car
from vector_math import linesCollided, vec2, unit_vector_from_angle
from racegame.config import windowHeight, windowWidth
from NEAT.Population import *
import time

def do_collide(track_limit, car):
    w = car.w
    h = car.l

    # print(track_limit['y2'])

    forward_vector = car.heading
    sideways_vector = vec2(car.heading).rotate(90)
    position = vec2(car.x, car.y)

    corners = []
    corner_multipliers = [[1, 1], [1, -1], [-1, -1], [-1, 1]]

    if track_limit['x'] == track_limit['x2']:
        track_limit['x'] += 1
    if track_limit['y'] == track_limit['y2']:
        track_limit['y'] += 1

    for i in range(4):
        corners.append(position + (sideways_vector * w / 2 * corner_multipliers[i][0]) + (forward_vector * h / 2 * corner_multipliers[i][1]))

    for i in range(4):
        j = i + 1
        j = j % 4
        if linesCollided(track_limit['x'], track_limit['y'], track_limit['x2'], track_limit['y2'], corners[i].x, corners[i].y, corners[j].x, corners[j].y):
            return True
    return False

class Game:

    def __init__(self, number_agents, max_generations, track_limits, reward_sectors, initial_x, initial_y, initial_heading, window):

        self.number_agents = number_agents
        self.agents = []
        self.track_limits = track_limits
        self.reward_sectors = reward_sectors
        self.max_generations = max_generations
        self.initial_x = initial_x
        self.initial_y = initial_y
        self.window = window
        self.initial_heading = unit_vector_from_angle(initial_heading)
        self.best_genome = None
        initial_genome_file = open('./Results/racecar-run-20230704-160557', 'rb')
        initial_genome = pickle.load(initial_genome_file)
        initial_genome_file.close()
        self.population = Population(self.number_agents, self.max_generations, self.determine_fitness, 13, 2, inject_genomes = [initial_genome])
        self.gen_text = pyglet.text.Label('Generation: 1',font_name='Century Gothic',font_size=15,bold=True,x=5, y=windowHeight - 5,anchor_x='left', anchor_y='top')
        self.score_text = pyglet.text.Label('Best score: 0',font_name='Century Gothic',font_size=15,bold=True,x=5, y=windowHeight - 25,anchor_x='left', anchor_y='top')
        self.species_text = pyglet.text.Label('Species: 0',font_name='Century Gothic',font_size=15,bold=True,x=5, y=windowHeight - 45,anchor_x='left', anchor_y='top')
        self.laps_text = pyglet.text.Label('Max Laps: 0',font_name='Century Gothic',font_size=15,bold=True,x=5, y=windowHeight - 65,anchor_x='left', anchor_y='top')
        self.population.run()

        genome_dump_file = open("./Results/racecar-run-" + time.strftime("%Y%m%d-%H%M%S"), 'wb')
        pickle.dump(self.population.best_genome, genome_dump_file)
        genome_dump_file.close()

    def render(self):

        self.gen_text.draw()
        self.score_text.draw()
        self.species_text.draw()
        self.laps_text.draw()
        if self.best_genome:
            self.draw_genome()
        for agent in self.agents:
            if agent.active:
                agent.draw()
                # agent.show_radar()

    def determine_fitness(self, genomes):

        # create agents with genomes (neural networks)
        # run for set amount of timesteps
        # add fitnesses to the genomes
        # return
        self.agents[:] = []

        for i in range(len(genomes)):
            genomes[i].fitness = 100
            self.agents.append(Car(genomes[i], self.initial_x, self.initial_y, self.initial_heading))

        for k in range(500 + self.population.generation_number * 25):
            if self.generation_finished():
                break
            
            for agent in self.agents:
                if agent.active:
                    next_reward_sector = self.reward_sectors[agent.next_sector]
                    agent.update(self.track_limits, next_reward_sector)

                    if agent.is_idling > 10:
                        agent.active = False

                    agent.brain.fitness -= 1
                    for track_limit in self.track_limits:
                        if do_collide(track_limit, agent):
                            agent.brain.fitness -= 100
                            agent.active = False
                            break
                    if do_collide(next_reward_sector, agent):
                        agent.next_sector += 1
                        if agent.next_sector == len(self.reward_sectors):
                            agent.next_sector = 0
                            agent.laps += 1
                        agent.brain.fitness += 100

                    if agent.brain.fitness <= 0:
                        agent.active = False
                        agent.brain.fitness = 1

            self.window.my_draw(self)
        best_fitness = 0
        best_brain = None
        for agent in self.agents:
            if agent.brain.fitness == 0:
                agent.brain.fitness = 0.1
            if agent.brain.fitness > best_fitness:
                best_fitness = agent.brain.fitness
                best_brain = agent.brain
        self.best_genome = best_brain
        # print(str(len(self.agents)) + " agents with best fitness of " + str(best_fitness))
        laps_finished = max([agent.laps for agent in self.agents])
        self.gen_text.text = "Generation: " + str(self.population.generation_number + 2)
        self.score_text.text = "Best score: " + str(best_fitness)
        self.species_text.text = "Species: " + str(len(self.population.species))
        self.laps_text.text = 'Max Laps: ' + str(laps_finished)

    def draw_genome(self):

        layers = set()
        draw_objects = []
        node_lookup = {}
        for node in self.best_genome.nodes:
            layers.add(node.layer)
        for layer in list(layers):
            x_pos = windowWidth - 20 - (1 - layer) * 100
            layer_nodes = self.best_genome.get_nodes_by_layer(layer)
            num_nodes = len(layer_nodes)
            for i in range(num_nodes):
                y_pos = windowHeight - 10 - ((i + 1) / (num_nodes + 1)) * 200
                node_lookup[layer_nodes[i].ID] = {"x": x_pos, "y": y_pos}
                if layer_nodes[i].type == "input" or layer_nodes[i].type == "output" or layer_nodes[i].type == "hidden":
                    color = (0, 0, 255)
                elif layer_nodes[i].type == "bias":
                    color = (248, 255, 48)
                node_circle = pyglet.shapes.Circle(x_pos, y_pos, 5, color = color)
                draw_objects.append(node_circle)

        for connection in self.best_genome.connections:
            origin_node = node_lookup[connection.origin_node_ID]
            target_node = node_lookup[connection.target_node_ID]
            if connection.origin_node_ID != connection.target_node_ID:
                x1 = origin_node['x']
                y1 = origin_node['y']
                x2 = target_node['x']
                y2 = target_node['y']
                size = max(1, int((abs(connection.weight) / 10) * 6))
                color = (0, 255, 0) if origin_node['x'] <= target_node['x'] else (255, 0, 0)
                color = (int(130 - connection.weight / 10 * 130), int(130 + connection.weight / 10 * 125), 0) if connection.weight >= 0 else (int(130 - connection.weight / 10 * 125), int(130 + connection.weight / 10 * 130), 0)
                connection_line = pyglet.shapes.Line(x1, y1, x2, y2, width = size, color = color)
                draw_objects.append(connection_line)
            else:
                x1 = origin_node['x']
                y1 = origin_node['y'] - 5
                x2 = origin_node['x'] + 10
                y2 = origin_node['y']
                x3 = origin_node['x']
                y3 = origin_node['y'] + 5
                size = max(1, int((abs(connection.weight) / 10) * 6))
                color = (0, 0, 255)
                connection_line1 = pyglet.shapes.Line(x1, y1, x2, y2, width = size, color = color)
                connection_line2 = pyglet.shapes.Line(x2, y2, x3, y3, width = size, color = color)
                draw_objects.append(connection_line1)
                draw_objects.append(connection_line2)

        for i in range(len(draw_objects)):
            draw_objects[len(draw_objects) - i - 1].draw()

    def generation_finished(self):

        for agent in self.agents:
            if agent.active:
                return False
        return True