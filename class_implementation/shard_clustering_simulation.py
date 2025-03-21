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
        for i in range(500, 1000)
    ]

    net.add_validator_node(more_nodes)

    client_nodes = [
        ClientNode(
            node_id=i,
            reputation_score=1,
            network=net,  # Pass the network instance here
            name=f"Client_{i}"
        )
        for i in range(100)
    ]

    for client_node in client_nodes:
        print(f"🛠️ Adding client: {client_node.node_id}, Type: {type(client_node)}") 
        net.add_client_node(client_node)

    print(net.shards)


if __name__ == '__main__':
    main()
