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

    def __init__(self, genome_id, innovation_history, nodes = None, connections = None, input_space = 2, output_space = 1):
    
        self.ID = genome_id
        self.species_ID = None
        self.innovation_history = innovation_history
        self.input_space = input_space
        self.output_space = output_space
        self.connections = connections
        self.nodes = nodes
        self.layers = None
        self.next_node_id = count(0)
        self.network = []
        self.fitness = 0
        self.adjusted_fitness = 0
        self.age = 0
        self.FSNEAT = False
        self.FDNEAT = False

        if nodes != None:
            if np.all([not c.enabled for c in connections]):
                pass
            self.nodes.sort(key=lambda x: x.ID)
            for i in range(len(self.nodes)):
                self.nodes[i].idx = i
            return
        
        self.nodes = []
        self.bias_node_id = next(self.next_node_id)
        bias_node = Node(self.bias_node_id, node_type = "bias", layer = 0.0)
        self.nodes.append(bias_node)
        
        for _ in range(input_space):
            node_ID = next(self.next_node_id)
            new_input_node = Node(node_ID, node_type = "input", layer = 0.0)
            self.nodes.append(new_input_node)

        for _ in range(output_space):
            node_ID = next(self.next_node_id)
            new_output_node = Node(node_ID, node_type = "output", layer = 1.0)
            self.nodes.append(new_output_node)

        innovation_history.next_node_id = max(innovation_history.next_node_id, next(self.next_node_id))

        if not self.FSNEAT:
            self.fully_connect()
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

    def is_good_pick(self, o, t):

        for connection in self.connections:
            if connection.origin_node_ID == o.ID and connection.target_node_ID == t.ID:
                return False
            
        return True

    def get_node_by_id(self, find_id):

        for node in self.nodes:
            if node.ID == find_id:
                return node
        return None
    
    def connect_nodes(self):

        layers = set()
        for node in self.nodes:
            node.outgoing_connections[:] = []
            node.incoming_connections[:] = []
            node.aggregated_inputs = 0
            node.activated_response = 0
            layers.add(node.layer)

        self.layers = len(layers)

        for connection in self.connections:
            if connection.enabled:
                target_node = self.get_node_by_id(connection.target_node_ID)
                origin_node = self.get_node_by_id(connection.origin_node_ID)
                target_node.incoming_connections.append(connection)
                origin_node.outgoing_connections.append(connection)
    
    def feed_forward(self, inputs):
        np.seterr(over='ignore')
        for _ in range(self.layers):
            outputs = []
            input_number = count(0)
            for node in self.nodes:
                if node.type == "input":
                    node.activated_response = inputs[next(input_number)]
                elif node.type == "bias":
                    node.activated_response = 1
                else:
                    node.fire(self)
                    if node.type == "output":
                        outputs.append(node.activated_response)
        return np.array(outputs)
    
    def fully_connect(self):
        self.connections = []
        input_nodes = self.get_zero_layer_nodes()
        output_nodes = self.get_output_nodes()
        for input_node in input_nodes:
            for output_node in output_nodes:
                innovation = self.innovation_history.get_innovation('connection', input_node.ID, output_node.ID)
                weight = np.random.normal(0, CONNECTION_CONFIG.STD_DEV_WEIGHT)
                new_connection = Connection(weight, input_node.ID, output_node.ID, innovation.innovation_ID)
                self.connections.append(new_connection)

    def partially_connect(self):
        self.connections = []
        input_node = random.choice(self.get_zero_layer_nodes())
        output_node = random.choice(self.get_output_nodes())
        innovation = self.innovation_history.get_innovation('connection', input_node.ID, output_node.ID)
        weight = np.random.normal(0, CONNECTION_CONFIG.STD_DEV_WEIGHT)
        new_connection = Connection(weight, input_node.ID, output_node.ID, innovation.innovation_ID)
        self.connections.append(new_connection)
    
    def build_network(self):

        self.connect_nodes()

    def add_node(self):
        
        random_connection = None
        size_threshold = self.input_space + self.output_space + 5

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

        origin_node = self.get_node_by_id(random_connection.origin_node_ID)
        target_node = self.get_node_by_id(random_connection.target_node_ID)
        new_layer = (origin_node.layer + target_node.layer) / 2
        recurrent = origin_node.layer > target_node.layer

        innovation = self.innovation_history.get_innovation('node', origin_node.ID, target_node.ID)

        new_node = self.get_node_by_id(innovation.node_id)

        if new_node == None:

            new_node = Node(innovation.node_id, node_type="hidden", layer = new_layer)
            self.nodes.append(new_node)

            innovation_connection_1 = self.innovation_history.get_innovation('connection', origin_node.ID, new_node.ID)
            new_connection_1 = Connection(1.0, origin_node.ID, new_node.ID, innovation_connection_1.innovation_ID, recurrent=recurrent)
            self.connections.append(new_connection_1)

            innovation_connection_2 = self.innovation_history.get_innovation('connection', new_node.ID, target_node.ID)
            new_connection_2 = Connection(random_connection.weight, new_node.ID, target_node.ID, innovation_connection_2.innovation_ID, recurrent=recurrent)
            self.connections.append(new_connection_2)

            random_connection.enabled = False

            return (new_node, new_connection_1, new_connection_2)
        else:
            return None
        
    def remove_connection(self):

        for _ in range(GENOME_CONFIG.FIND_LINK_TRIES):
            random_connection = random.choice(self.connections)

            if self.get_node_by_id(random_connection.origin_node_ID).type in ["input", "bias"] and self.get_node_by_id(random_connection.target_node_ID).type == "output":
                self.connections.remove(random_connection)

    def add_connection(self):

        random_node_1 = random_node_2 = None

        if random_node_1 == None:
            for _ in range(GENOME_CONFIG.FIND_UNLINKED_NODES_TRIES):
                # trial_node_1, trial_node_2 = random.sample(self.nodes, 2)
                trial_node_1 = self.nodes[random.randint(0,len(self.nodes)-1)]
                trial_node_2 = self.nodes[random.randint(1+self.input_space,len(self.nodes)-1)]

                if self.is_good_pick(trial_node_1, trial_node_2):
                    if trial_node_1.layer >= trial_node_2.layer:
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

        innovation = self.innovation_history.get_innovation('connection', random_node_1.ID, random_node_2.ID)
        weight = np.random.normal(0, CONNECTION_CONFIG.STD_DEV_WEIGHT)
        new_connection = Connection(weight, random_node_1.ID, random_node_2.ID, innovation.innovation_ID, recurrent=recurrent)
        self.connections.append(new_connection)

        return new_connection

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

        if self.FDNEAT:
            probability_value = random.random()
            if probability_value < GENOME_CONFIG.MUTATION_DESELECTION:
                self.remove_connection()