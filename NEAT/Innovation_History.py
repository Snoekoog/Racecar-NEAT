from itertools import count
from .Node import Node

class Innovation():

    def __init__(self, innovation_id: int, innovation_type: str, origin_node_ID: int = None, target_node_ID: int = None, node_ID: int = None, connection_ID: int = None):

        self.type               = innovation_type   # Type of innovation
        self.innovation_ID      = innovation_id     # ID of innovation
        self.origin_node_ID     = origin_node_ID    # ID of origin node
        self.target_node_ID     = target_node_ID    # ID of target node
        self.node_id            = node_ID           # Node ID of innovation
        self.connection_id      = connection_ID     # Connection ID of innovation

class Innovation_History():

    def __init__(self):
        self.next_innovation_id = 0                 # Next innovation ID
        self.next_node_id       = 0                 # Next node ID
        self.next_connection_id = 0                 # Next connection ID
        self.innovations        = []                # List of innovations in history

    # Check to see if this innovation has already happened
    def exist_innovation(self, innovation_type, origin_node_ID: int, target_node_ID: int):

        # Loop through innovations in history
        for innovation in self.innovations:

            # If it all matches, return the corresponding innovation
            if innovation.type == innovation_type and innovation.origin_node_ID == origin_node_ID and innovation.target_node_ID == target_node_ID:
                return innovation
            
        # If not, return None
        return None

    # Create innovation because it did not exist yet
    def create_innovation(self, innovation_type: str, origin_node_ID: int = None, target_node_ID: int = None):
        
        # If not everything is supplied we error
        if origin_node_ID == None or target_node_ID == None:
            return None
        
        # If we need to create an innovation for a new node
        if innovation_type == 'node':
            new_innovation = Innovation(self.next_innovation_id, innovation_type, origin_node_ID, target_node_ID, node_ID = self.next_node_id)
            self.next_node_id += 1

        # Else
        elif innovation_type == 'connection':
            new_innovation = Innovation(self.next_innovation_id, innovation_type, origin_node_ID, target_node_ID, connection_ID = self.next_connection_id)
            self.next_connection_id += 1
        else:
            return None
        
        # Add to history, increase innovation_id count and return innovation
        self.innovations.append(new_innovation)
        self.next_innovation_id += 1
        return new_innovation
    
    # Check to see if innovation exists, otherwise make new one
    def get_innovation(self, innovation_type: str, origin_node_ID: int = None, target_node_ID: int = None):
        innovation = self.exist_innovation(innovation_type, origin_node_ID, target_node_ID)
        if innovation == None:
            innovation = self.create_innovation(innovation_type, origin_node_ID, target_node_ID)
        return innovation
        