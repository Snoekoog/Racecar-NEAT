from .config import CONNECTION_CONFIG
import random
import numpy as np

class Connection:

    def __init__(self, weight: float, origin_node_ID: int, target_node_ID: int, innovation_number: int, recurrent: bool = False):

        self.origin_node_ID = origin_node_ID
        self.target_node_ID = target_node_ID
        self.recurrent = recurrent
        self.weight = weight
        self.enabled = True
        self.innovation_number = innovation_number

    def mutate(self):

        if random.random() < CONNECTION_CONFIG.MUTATE_RESET:
            self.weight = np.random.normal(0, CONNECTION_CONFIG.STD_DEV_WEIGHT)
        else:
            weight_change = np.random.normal(0, CONNECTION_CONFIG.STD_DEV_WEIGHT_VAR)
            self.weight += weight_change
            self.weight = np.clip(self.weight, CONNECTION_CONFIG.MIN_WEIGHT, CONNECTION_CONFIG.MAX_WEIGHT)