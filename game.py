import pyglet
from pyglet.gl import *
from racegame.car import Car
from vector_math import unit_vector_from_angle, do_collide
from racegame.config import windowHeight, windowWidth
from NEAT.Population import *
import time

class Game:

    def __init__(self, number_agents: int, max_generations: int, track_limits: list, reward_sectors: list, initial_x: int, initial_y: int, initial_heading: float, window):

        self.number_agents      = number_agents                             # Number of agents (genomes) to consider = population size
        self.agents             = []                                        # List of agents
        self.track_limits       = track_limits                              # List of track limit lines
        self.reward_sectors     = reward_sectors                            # List of reward sector lines
        self.max_generations    = max_generations                           # Max number of generations
        self.initial_x          = initial_x                                 # Start x position
        self.initial_y          = initial_y                                 # Start y position
        self.window             = window                                    # Window to draw stuff to
        self.initial_heading    = unit_vector_from_angle(initial_heading)   # Initial heading unit vector
        self.best_genome        = None                                      # Best genome found so far
        self.stop_on_lap        = False                                     # Stop when a lap is finished by at least one agent
        self.champion_id        = None                                      # ID of champion (best genome)

        # Open genome file of genome to inject. Load it using Pickle
        initial_genome_file = open('./Results/silverstone-transfer-redbullring-transfer-spa', 'rb')
        initial_genome = pickle.load(initial_genome_file)
        initial_genome_file.close()

        # Create population (or well, NEAT instance)
        self.population     = Population(self.number_agents, self.max_generations, self.determine_fitness, 11, 2, inject_genomes = None)

        # Create text objects to display on screen
        self.gen_text       = pyglet.text.Label('Generation: 1',font_name='Century Gothic',font_size=15,bold=True,x=5, y=windowHeight - 5,anchor_x='left', anchor_y='top')
        self.score_text     = pyglet.text.Label('Best score: 0',font_name='Century Gothic',font_size=15,bold=True,x=5, y=windowHeight - 25,anchor_x='left', anchor_y='top')
        self.species_text   = pyglet.text.Label('Species: 0',font_name='Century Gothic',font_size=15,bold=True,x=5, y=windowHeight - 45,anchor_x='left', anchor_y='top')
        self.laps_text      = pyglet.text.Label('Max Laps: 0',font_name='Century Gothic',font_size=15,bold=True,x=5, y=windowHeight - 65,anchor_x='left', anchor_y='top')

        # Run NEAT
        self.population.run()

        # Below is what will happen AFTER NEAT is finished. So, save best genome to a file using Pickle
        genome_dump_file = open("./Results/racecar-run-" + time.strftime("%Y%m%d-%H%M%S"), 'wb')
        pickle.dump(self.population.best_genome, genome_dump_file)
        genome_dump_file.close()

    # Render function: render everything for the current timestep to the window
    def render(self):

        # Draw all texts
        self.gen_text.draw()
        self.score_text.draw()
        self.species_text.draw()
        self.laps_text.draw()

        # If we have a best genome (which we should, after generation 1): draw it to screen
        if self.best_genome:
            self.draw_genome()

        # Loop through each agent and draw them all
        for agent in self.agents:
            if agent.active:
                agent.draw()

                # Optional: draw radar measurement points (is slower though)
                # agent.show_radar()

    # Determine fitness of the genomes
    def determine_fitness(self, genomes: list[Genome]):

        # Reset list of agents
        self.agents[:] = []

        # For each supplied genome
        for i in range(len(genomes)):

            # Set its initial fitness to 100
            genomes[i].fitness = 100

            # Is this genome the champion of the previous round? (used for setting the champion car from elitism to blue)
            is_champion = genomes[i].ID == self.champion_id

            # Create agent (car) with that genome as brain
            self.agents.append(Car(genomes[i], self.initial_x, self.initial_y, self.initial_heading, is_champion))

        # For 500 + n * 25 timesteps
        for k in range(500 + self.population.generation_number * 25):

            # If generation is finished, simply stop looping
            if self.generation_finished():
                break
            
            # Loop through agents
            for agent in self.agents:

                # Only do stuff if the agent is active
                if agent.active:

                    # Get next reward sector line from list
                    next_reward_sector = self.reward_sectors[agent.next_sector]

                    # Update movement of the agent
                    agent.update(self.track_limits, next_reward_sector)

                    # If it's been idling for more than 10 timesteps, deactivate it
                    if agent.is_idling > 10:
                        agent.active = False

                    # Every time-step, remove 1 from its fitness
                    agent.brain.fitness -= 1

                    # Loop through track limits
                    for track_limit in self.track_limits:

                        # Check for collisions
                        if do_collide(track_limit, agent):

                            # If collided, penalise with -100 fitness and deactivate agent
                            agent.brain.fitness -= 100
                            agent.active = False
                            break

                    # Check for collision with next reward sector (good thing!)
                    if do_collide(next_reward_sector, agent):

                        # If so, update its next sector number
                        agent.next_sector += 1

                        # Loop around if we reached the end of the track
                        if agent.next_sector == len(self.reward_sectors):
                            agent.next_sector = 0
                            agent.laps += 1

                        # And of course, reward it with 100 fitness
                        agent.brain.fitness += 100

                    # If agent dips below 0 fitness, limit it to 1 but deactivate the agent
                    if agent.brain.fitness <= 0:
                        agent.active = False
                        agent.brain.fitness = 1

            # Use window's my draw function
            self.window.my_draw(self)

        # Temporary variables
        best_fitness = 0
        best_brain = None

        # Loop through agents
        for agent in self.agents:

            # If it's better than the previous best, update best fitness and best genome
            if agent.brain.fitness > best_fitness:
                best_fitness = agent.brain.fitness
                best_brain = agent.brain

        # Update best genome
        self.best_genome = best_brain

        # Max nr of laps finished
        laps_finished = max([agent.laps for agent in self.agents])

        # Has any agent finished a lap yet?
        is_finished = any([agent.laps > 0 for agent in self.agents]) and self.stop_on_lap

        # Update texts on screen
        self.gen_text.text      = "Generation: " + str(self.population.generation_number + 2)
        self.score_text.text    = "Best score: " + str(best_fitness)
        self.species_text.text  = "Species: " + str(len(self.population.species))
        self.laps_text.text     = 'Max Laps: ' + str(laps_finished)

        # Store ID of best genome to determine next generations champion agent
        self.champion_id = self.best_genome.ID

        # Return is_finished to NEAT
        return is_finished

    # Draw best performing network so far to screen
    def draw_genome(self):

        # Set of layer numbers
        layers = set()

        # List of objects to draw to screen
        draw_objects = []

        # Create lookup dict for node positions
        node_lookup = {}

        # Create a set of layer numbers
        for node in self.best_genome.nodes:
            layers.add(node.layer)

        # Loop through layers
        for layer in list(layers):

            # Determine x pos
            x_pos = windowWidth - 20 - (1 - layer) * 100

            # Determine number of nodes in this later
            layer_nodes = self.best_genome.get_nodes_by_layer(layer)

            # Number of nodes in this layer
            num_nodes = len(layer_nodes)

            # Loop through number
            for i in range(num_nodes):

                # Determine y pos
                y_pos = windowHeight - 10 - ((i + 1) / (num_nodes + 1)) * 200

                # Store it in node lookup table
                node_lookup[layer_nodes[i].ID] = {"x": x_pos, "y": y_pos}

                # if input, output or hidden, set color to blue
                if layer_nodes[i].type == "input" or layer_nodes[i].type == "output" or layer_nodes[i].type == "hidden":
                    color = (0, 0, 255)

                # if bias, color it yellow
                elif layer_nodes[i].type == "bias":
                    color = (248, 255, 48)

                # Create circle object for that node and store it in objects to be drawn list
                node_circle = pyglet.shapes.Circle(x_pos, y_pos, 5, color = color)
                draw_objects.append(node_circle)

        # Loop through connections
        for connection in self.best_genome.connections:

            # Get origin node and target node locations from node lookup table
            origin_node = node_lookup[connection.origin_node_ID]
            target_node = node_lookup[connection.target_node_ID]

            # If the connection is between different nodes
            if connection.origin_node_ID != connection.target_node_ID:

                # Extract locations for start and end point of line
                x1 = origin_node['x']
                y1 = origin_node['y']
                x2 = target_node['x']
                y2 = target_node['y']

                # Calculate size (bigger = larger weight)
                size = max(1, int((abs(connection.weight) / 10) * 6))

                # Color it according to weight (negative = red, positive = green, gradient inbetween)
                color = (0, 255, 0) if origin_node['x'] <= target_node['x'] else (255, 0, 0)
                color = (int(130 - connection.weight / 10 * 130), int(130 + connection.weight / 10 * 125), 0) if connection.weight >= 0 else (int(130 - connection.weight / 10 * 125), int(130 + connection.weight / 10 * 130), 0)

                # Create line object for connection and add it to draw-object list
                connection_line = pyglet.shapes.Line(x1, y1, x2, y2, width = size, color = color)
                draw_objects.append(connection_line)
            else:

                # Connection is to itself, so just make a small triangle shape connection
                x1 = origin_node['x']
                y1 = origin_node['y'] - 5
                x2 = origin_node['x'] + 10
                y2 = origin_node['y']
                x3 = origin_node['x']
                y3 = origin_node['y'] + 5

                # Calculate size according to weight
                size = max(1, int((abs(connection.weight) / 10) * 6))

                # Color it blue
                color = (0, 0, 255)

                # Create two lines for triangle and add to list
                connection_line1 = pyglet.shapes.Line(x1, y1, x2, y2, width = size, color = color)
                connection_line2 = pyglet.shapes.Line(x2, y2, x3, y3, width = size, color = color)
                draw_objects.append(connection_line1)
                draw_objects.append(connection_line2)

        # Do reverse loop through objects to be drawn to draw nodes on top of connections (looks better)
        for i in range(len(draw_objects)):
            draw_objects[len(draw_objects) - i - 1].draw()

    # Is generation finished?
    def generation_finished(self):

        # Only if there is at least one agent still active!
        for agent in self.agents:
            if agent.active:
                return False
        return True