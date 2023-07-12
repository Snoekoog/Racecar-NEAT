from itertools import count
from .Node import Node
import random
from .Connection import Connection
from .Innovation_History import Innovation_History
from .config import GENOME_CONFIG, CONNECTION_CONFIG
import numpy as np
import math as m
import time

class Genome:

    def __init__(self, genome_id: int, innovation_history: Innovation_History, nodes:list[Node] = None, connections:list[Connection] = None, input_space: int = 2, output_space: int = 1):
    
        self.ID                     = genome_id             # ID of genome
        self.species_ID             = None                  # Species ID the genome is part of
        self.innovation_history     = innovation_history    # Innovation history of the population
        self.input_space            = input_space           # Number of inputs
        self.output_space           = output_space          # Number of outputs
        self.connections            = connections           # Connections of genome/network
        self.nodes                  = nodes                 # Nodes of genome/network
        self.layers                 = None                  # Number of layers in network
        self.next_node_id           = count(0)              # Counter for next node id
        self.network                = []                    # (UNUSED) phenotype
        self.fitness                = 0                     # Fitness of genome
        self.adjusted_fitness       = 0                     # (UNUSED) adjusted fitness of genome (for fitness sharing)
        self.age                    = 0                     # Age of genome
        self.FSNEAT                 = False                 # FSNEAT enabled?
        self.FDNEAT                 = False                 # FDNEAT enabled? NOTE: do not simultaneously enable FSNEAT and FDNEAT!

        # If a set of nodes is supplied
        if nodes != None:

            # Check if they are all enabled. Otherwise, it's a useless network: then pass and create a new network
            if np.all([not c.enabled for c in connections]):
                pass

            # Sort by ID (useful for order in feed forward later)
            self.nodes.sort(key=lambda x: x.ID)

            # No need to do the rest of the initialisation. Return to stop it!
            return
        
        # Empty nodes
        self.nodes = []

        # NOTE: layers are between 0 and 1! Input = 0, output = 1, hidden is between.
        # For example: network with 2 hidden layers will have layers 0, 0.333, 0.666, 1.
        
        # Get next node id, which will also be the ID of the bias. Create bias node in layer 0 and add
        self.bias_node_id = next(self.next_node_id)
        bias_node = Node(self.bias_node_id, node_type = "bias", layer = 0.0)
        self.nodes.append(bias_node)
        
        # For each input node, create a node in layer 0 and add it
        for _ in range(input_space):
            node_ID = next(self.next_node_id)
            new_input_node = Node(node_ID, node_type = "input", layer = 0.0)
            self.nodes.append(new_input_node)

        # For each output node, create a node in layer 1 and add it
        for _ in range(output_space):
            node_ID = next(self.next_node_id)
            new_output_node = Node(node_ID, node_type = "output", layer = 1.0)
            self.nodes.append(new_output_node)

        # Set innovation history's node id to what comes next
        innovation_history.next_node_id = max(innovation_history.next_node_id, next(self.next_node_id))

        # If normal NEAT, fully connect
        if not self.FSNEAT:
            self.fully_connect()
        # Otherwise only partially connect
        else:
            self.partially_connect()

    def get_zero_layer_nodes(self):
        return [node for node in self.nodes if node.type in ["input", "bias"]]
    
    def get_input_nodes(self):
        return [node for node in self.nodes if node.type in ["input"]]
    
    def get_hidden_nodes(self):
        return [node for node in self.nodes if node.type in ["hidden"]]
    
    def get_output_nodes(self):
        return [node for node in self.nodes if node.type in ["output"]]
    
    def get_bias_nodes(self):
        return [node for node in self.nodes if node.type in ["bias"]]
    
    def get_edge_nodes(self):
        return [node for node in self.nodes if node.type in ["input", "bias", "output"]]
    
    def get_nodes_by_layer(self, layer):
        return [node for node in self.nodes if node.layer == layer]

    # Figure out of two nodes are not previously connected
    def is_good_pick(self, o: Node, t: Node):

        for connection in self.connections:
            if connection.origin_node_ID == o.ID and connection.target_node_ID == t.ID:
                return False
            
        return True

    # Get node from network by node id
    def get_node_by_id(self, find_id):

        for node in self.nodes:
            if node.ID == find_id:
                return node
        return None
    
    # Setup all nodes and connections correctly so feed forward works good
    def connect_nodes(self):

        # All layers that are present in the genome. Set because we do not want duplicates
        layers = set()

        # Loop through nodes
        for node in self.nodes:

            # Reset incoming and outgoing connections, input value and output value. Add layer to the set
            node.outgoing_connections[:] = []
            node.incoming_connections[:] = []
            node.aggregated_inputs = 0
            node.activated_response = 0
            layers.add(node.layer)

        # Logically, number of layers is number of unique layers in the set
        self.layers = len(layers)

        # Loop through connections
        for connection in self.connections:
            if connection.enabled:

                # Add connection to the right nodes
                target_node = self.get_node_by_id(connection.target_node_ID)
                origin_node = self.get_node_by_id(connection.origin_node_ID)
                target_node.incoming_connections.append(connection)
                origin_node.outgoing_connections.append(connection)
    
    # Feed forward function (i.e. to make the network 'think')
    def feed_forward(self, inputs):

        # Ignore those annoying overflow errors. Grr!
        np.seterr(over='ignore')

        # Loop through number of layers ('Flushing' of the network - prevents us from having to do everything in order)
        for _ in range(self.layers):

            # Accumulator for outputs
            outputs = []

            # idx for inputs
            input_number = count(0)

            # Loop through nodes
            for node in self.nodes:

                if node.type == "input":

                    # If it's an input node, we can set its output value to the input value
                    node.activated_response = inputs[next(input_number)]

                elif node.type == "bias":

                    # If it's a bias node, it's output value is just one
                    node.activated_response = 1
                else:

                    # Fire the node! (use activation function on accumulated inputs)
                    node.fire(self)

                    # If it's an output node, add the output to the list
                    if node.type == "output":
                        outputs.append(node.activated_response)

        # Return the list as a Numpy array
        return np.array(outputs)
    
    # Standard NEAT: fully connect!
    def fully_connect(self):

        # Reset connections
        self.connections = []

        # Get all layer 0 nodes
        input_nodes = self.get_zero_layer_nodes()

        # Get all layer 1 nodes
        output_nodes = self.get_output_nodes()

        # Loop through both input and output nodes to get all pairs
        for input_node in input_nodes:
            for output_node in output_nodes:

                # Get innovation from history
                innovation = self.innovation_history.get_innovation('connection', input_node.ID, output_node.ID)

                # Create new weight
                weight = np.random.normal(0, CONNECTION_CONFIG.STD_DEV_WEIGHT)

                # Create new connection
                new_connection = Connection(weight, input_node.ID, output_node.ID, innovation.innovation_ID)

                # Add to network
                self.connections.append(new_connection)

    # FSNEAT: partially connect!
    def partially_connect(self):

        # Reset connections
        self.connections = []

        # Choose random input node
        input_node = random.choice(self.get_zero_layer_nodes())

        # Choose random output node
        output_node = random.choice(self.get_output_nodes())

        # Get innovation from history
        innovation = self.innovation_history.get_innovation('connection', input_node.ID, output_node.ID)

        # Create new weight
        weight = np.random.normal(0, CONNECTION_CONFIG.STD_DEV_WEIGHT)

        # Create new connection
        new_connection = Connection(weight, input_node.ID, output_node.ID, innovation.innovation_ID)

        # Add to network
        self.connections.append(new_connection)
    
    def build_network(self):

        self.connect_nodes()

    # Mutation: add node
    def add_node(self):
        
        # Placeholder for randomly chosen connection
        random_connection = None
        size_threshold = self.input_space + self.output_space + 5

        # Logic for trying to find a connection
        if len(self.connections) < size_threshold:
            for _ in range(GENOME_CONFIG.FIND_LINK_TRIES):
                trial_connection = self.connections[random.randint(0,len(self.connections)-1-int(m.sqrt(len(self.connections)-1)))]
                if trial_connection.enabled and not trial_connection.recurrent and self.get_node_by_id(trial_connection.origin_node_ID).type != "bias":
                    random_connection = trial_connection
                    break
            if random_connection == None:
                return
        else:
            while random_connection == None:
                trial_connection = random.choice(self.connections)
                if trial_connection.enabled and not trial_connection.recurrent and self.get_node_by_id(trial_connection.origin_node_ID).type != "bias":
                    random_connection = trial_connection

        # Get origin and target node
        origin_node = self.get_node_by_id(random_connection.origin_node_ID)
        target_node = self.get_node_by_id(random_connection.target_node_ID)

        # Set new layer (between the two nodes from above)
        new_layer = (origin_node.layer + target_node.layer) / 2

        # Is recurrent?
        recurrent = origin_node.layer > target_node.layer

        # Get innovation from history
        innovation = self.innovation_history.get_innovation('node', origin_node.ID, target_node.ID)

        # Does this node already exist?
        new_node = self.get_node_by_id(innovation.node_id)

        # If not
        if new_node == None:

            # Create it!
            new_node = Node(innovation.node_id, node_type="hidden", layer = new_layer)
            self.nodes.append(new_node)

            # Add new connection between old origin and new node
            innovation_connection_1 = self.innovation_history.get_innovation('connection', origin_node.ID, new_node.ID)
            new_connection_1 = Connection(1.0, origin_node.ID, new_node.ID, innovation_connection_1.innovation_ID, recurrent=recurrent)
            self.connections.append(new_connection_1)

            # add connection between new node and old target
            innovation_connection_2 = self.innovation_history.get_innovation('connection', new_node.ID, target_node.ID)
            new_connection_2 = Connection(random_connection.weight, new_node.ID, target_node.ID, innovation_connection_2.innovation_ID, recurrent=recurrent)
            self.connections.append(new_connection_2)

            # Disable old connection
            random_connection.enabled = False
        else:
            return None
        
    # For FDNEAT: remove a connection
    def remove_connection(self):

        # Try a set amount of times
        for _ in range(GENOME_CONFIG.FIND_LINK_TRIES):
            random_connection = random.choice(self.connections)

            # If the connection qualifies, remove it
            if self.get_node_by_id(random_connection.origin_node_ID).type in ["input", "bias"] and self.get_node_by_id(random_connection.target_node_ID).type == "output":
                self.connections.remove(random_connection)
                break

    # Mutation: add connection
    def add_connection(self):

        # Placeholder for connections
        random_node_1 = random_node_2 = None

        if random_node_1 == None:
            for _ in range(GENOME_CONFIG.FIND_UNLINKED_NODES_TRIES):

                # Try two nodes
                trial_node_1 = self.nodes[random.randint(0,len(self.nodes)-1)]
                trial_node_2 = self.nodes[random.randint(1+self.input_space,len(self.nodes)-1)]

                # If they are a good pick (no connection yet)
                if self.is_good_pick(trial_node_1, trial_node_2):

                    # If recurrent
                    if trial_node_1.layer >= trial_node_2.layer:

                        # Only accept sometimes
                        if random.random() < GENOME_CONFIG.MUTATION_ADD_RECURRENT:
                            random_node_1 = trial_node_1
                            random_node_2 = trial_node_2
                            recurrent = True
                            break
                    else:
                        random_node_1 = trial_node_1
                        random_node_2 = trial_node_2
                        recurrent = False
                        break

        if random_node_1 == None or random_node_2 == None:
            return None

        # Create new connection between the two
        innovation = self.innovation_history.get_innovation('connection', random_node_1.ID, random_node_2.ID)
        weight = np.random.normal(0, CONNECTION_CONFIG.STD_DEV_WEIGHT)
        new_connection = Connection(weight, random_node_1.ID, random_node_2.ID, innovation.innovation_ID, recurrent=recurrent)
        self.connections.append(new_connection)

    # Full mutation step
    def mutate(self):

        probability_value = random.random()
        if probability_value < GENOME_CONFIG.MUTATION_ADD_NODE:
            self.add_node()

        probability_value = random.random()
        if probability_value < GENOME_CONFIG.MUTATION_ADD_CONNECTION:
            self.add_connection()

        for connection in self.connections:
            probability_value = random.random()
            if probability_value < GENOME_CONFIG.MUTATION_WEIGHT:
                connection.mutate()

        for node in self.nodes:
            probability_value = random.random()
            if probability_value < GENOME_CONFIG.MUTATION_ACTIVATION:
                node.activation_response += (random.random()*2-1) * GENOME_CONFIG.MUTATION_ACTIVATION_PERTURBATION

        if self.FDNEAT and len(self.connections) > 1:
            probability_value = random.random()
            if probability_value < GENOME_CONFIG.MUTATION_DESELECTION:
                self.remove_connection()