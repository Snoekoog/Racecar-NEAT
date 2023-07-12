from .config import CONNECTION_CONFIG
import random
import numpy as np

class Connection:

    def __init__(self, weight: float, origin_node_ID: int, target_node_ID: int, innovation_number: int, recurrent: bool = False):

        self.origin_node_ID     = origin_node_ID        # ID of origin node
        self.target_node_ID     = target_node_ID        # ID of target node
        self.recurrent          = recurrent             # Is recurrent?
        self.weight             = weight                # Weight of connection
        self.enabled            = True                  # Is it enabled?
        self.innovation_number  = innovation_number     # Innovation number of connection


    # Mutate this connection, called from Genome
    def mutate(self):

        # Reset weight entirely
        if random.random() < CONNECTION_CONFIG.MUTATE_RESET:
            
            # Sample from normal distribution with weight reset standard deviation
            self.weight = np.random.normal(0, CONNECTION_CONFIG.STD_DEV_WEIGHT)

        # Only adjust weight a bit
        else:

            # Compute change in weight by sampling from normal distribution with weight adjustment standard deviation
            weight_change = np.random.normal(0, CONNECTION_CONFIG.STD_DEV_WEIGHT_VAR)

            # Add to weight
            self.weight += weight_change

            # Make sure it is within limits
            self.weight = np.clip(self.weight, CONNECTION_CONFIG.MIN_WEIGHT, CONNECTION_CONFIG.MAX_WEIGHT)