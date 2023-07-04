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

        if self.type not in ['bias', 'input']:
            self.activate(self.aggregated_inputs)

        for connection in self.outgoing_connections:
            if connection.enabled:
                target_node = genome.get_node_by_id(connection.target_node_ID)
                target_node.aggregated_inputs += connection.weight * self.activated_response

    def activate(self, x: float):

        if self.activation_type == 'Sigmoid':
            self.activated_response = 1 / (1 + np.exp(-x))
        elif self.activation_type == "ScaledSigmoid":
            self.activated_response = (1.0 / (1.0 + np.exp(-self.aggregated_inputs/self.activation_response))) * 2.0 - 1.0
        elif self.activation_type == 'ReLu':
            self.activated_response = max(0, x)
        elif self.activation_type == 'LeakyReLu':
            self.activated_response = max(0.1*x, x)
        elif self.activation_type == 'Step':
            self.activated_response = float(x >= 0)
        else:
            self.activated_response = x
