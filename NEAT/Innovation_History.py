from itertools import count
from .Node import Node

class Innovation():

    def __init__(self, innovation_id: int, innovation_type: str, origin_node_ID = None, target_node_ID = None, node_ID = None, connection_ID = None):

        self.type = innovation_type
        self.innovation_ID = innovation_id
        self.origin_node_ID = origin_node_ID
        self.target_node_ID = target_node_ID
        self.node_id = node_ID
        self.connection_id = connection_ID

class Innovation_History():

    def __init__(self):
        self.next_innovation_id = 0
        self.next_node_id = 0
        self.next_connection_id = 0
        self.innovations = []

    def exist_innovation(self, innovation_type, origin_node_ID: int, target_node_ID: int):
        for innovation in self.innovations:
            if innovation.type == innovation_type and innovation.origin_node_ID == origin_node_ID and innovation.target_node_ID == target_node_ID:
                return innovation
        return None

    def create_innovation(self, innovation_type: str, origin_node_ID: int = None, target_node_ID: int = None):
        
        if origin_node_ID == None or target_node_ID == None:
            return None
        
        if innovation_type == 'node':
            new_innovation = Innovation(self.next_innovation_id, innovation_type, origin_node_ID, target_node_ID, node_ID = self.next_node_id)
            self.next_node_id += 1
        elif innovation_type == 'connection':
            new_innovation = Innovation(self.next_innovation_id, innovation_type, origin_node_ID, target_node_ID, connection_ID = self.next_connection_id)
            self.next_connection_id += 1
        else:
            return None
        
        self.innovations.append(new_innovation)
        self.next_innovation_id += 1
        return new_innovation
    
    def get_innovation(self, innovation_type: str, origin_node_ID: int = None, target_node_ID: int = None):
        innovation = self.exist_innovation(innovation_type, origin_node_ID, target_node_ID)
        if innovation == None:
            innovation = self.create_innovation(innovation_type, origin_node_ID, target_node_ID)
        return innovation
        