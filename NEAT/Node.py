import numpy as np
from .config import NODE_CONFIG

class Node():

    def __init__(self, ID: int, node_type: str, layer: float, activation_type: str = NODE_CONFIG.STANDARD_ACTIVATION_TYPE, activation_response: float = NODE_CONFIG.STANDARD_ACTIVATION_RESPONSE):

        self.ID = ID
        self.layer = layer
        self.type = node_type
        self.aggregated_inputs = 0
        self.activated_response = 0
        self.activation_type = activation_type
        self.activation_response = activation_response
        self.outgoing_connections = []
        self.incoming_connections = []

    def fire(self, genome):

        self.aggregated_inputs = 0.0
        for connection in self.incoming_connections:
            if connection.enabled:
                origin_node = genome.get_node_by_id(connection.origin_node_ID)
                self.aggregated_inputs += connection.weight * origin_node.activated_response

        self.activate(self.aggregated_inputs)

    def activate(self, x: float):

        if self.activation_type == 'Sigmoid':
            self.activated_response = 1 / (1 + np.exp(-x))
        elif self.activation_type == "ScaledSigmoid":
            self.activated_response = (1.0 / (1.0 + np.exp(-x/self.activation_response))) * 2.0 - 1.0
        elif self.activation_type == 'ReLu':
            self.activated_response = max(0, x)
        elif self.activation_type == 'LeakyReLu':
            self.activated_response = max(0.1*x, x)
        elif self.activation_type == 'Step':
            self.activated_response = float(x >= 0)
        else:
            self.activated_response = x
