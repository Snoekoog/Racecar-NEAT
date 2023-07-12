import numpy as np
from .config import NODE_CONFIG

class Node():

    def __init__(self, ID: int, node_type: str, layer: float, activation_type: str = NODE_CONFIG.STANDARD_ACTIVATION_TYPE, activation_response: float = NODE_CONFIG.STANDARD_ACTIVATION_RESPONSE):

        self.ID                     = ID                    # ID of node
        self.layer                  = layer                 # Layer the node is in
        self.type                   = node_type             # Type of node [input, output, bias, hidden]
        self.aggregated_inputs      = 0                     # Inputs from incoming connections
        self.activated_response     = 0                     # Input put through activation
        self.activation_type        = activation_type       # Type of activation function
        self.activation_response    = activation_response   # Sigmoid slope
        self.outgoing_connections   = []                    # (UNUSED) List of outgoing connections
        self.incoming_connections   = []                    # List of incoming connections

    # Fire! (e.g. put inputs through activation)
    def fire(self, genome):

        # Reset inputs
        self.aggregated_inputs = 0.0

        # Loop through incoming connections
        for connection in self.incoming_connections:

            if connection.enabled:

                # Gather inputs
                origin_node = genome.get_node_by_id(connection.origin_node_ID)
                self.aggregated_inputs += connection.weight * origin_node.activated_response

        # Then activate!
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
