import random
class DummyNode:
    def __init__(self, node_id, cpu_rating, reputation_score, ram_usage):
        self.node_id = node_id
        self.cpu_rating = cpu_rating
        self.reputation_score = reputation_score
        self.ram_usage = ram_usage

    def __repr__(self):
        return f"Node(id={self.node_id}, cpu_rating={self.cpu_rating}, reputation_score={self.reputation_score})"

class DummyNetwork:
    def __init__(self, nodes):
        self.validator_nodes = nodes


