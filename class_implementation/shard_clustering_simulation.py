import random
from validator_node import ValidatorNode
from client_node import ClientNode
from shard import Shard
from network import Network

def main():
    N = 500
    random.seed(42)
    
    # Create a network instance first
    net = Network(s_min=3, s_max=20, lambda_val=0.4, byzantine_threshold=0.3)
    
    nodes = [
        ValidatorNode(
            node_id=i,
            cpu_rating=random.uniform(1, 10),
            reputation_score=random.uniform(0, 1),
            ram_usage=random.uniform(1, 16),
            network=net,  # Pass the network instance here
            name=f"Validator_{i}"
        )
        for i in range(N)
    ]
    
    net.add_validator_node(nodes)
    
    more_nodes = [
        ValidatorNode(
            node_id=i,
            cpu_rating=random.uniform(1, 10),
            reputation_score=random.uniform(0, 1),
            ram_usage=random.uniform(1, 16),
            network=net,  # Pass the network instance here
            name=f"Validator_{i}"
        )
        for i in range(500)
    ]

    net.add_validator_node(more_nodes)



if __name__ == '__main__':
    main()
