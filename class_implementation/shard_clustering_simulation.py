from validator_node import ValidatorNode
from client_node import ClientNode
from shard import Shard
from network import Network
import random

def main():
    val_nodes = []

    network = Network(min_nodes_per_shard=3, max_nodes_per_shard = 10)
    for i in range(0, 32):
        val_nodes.append(ValidatorNode(node_id=i, name= f"Validator_{i}", cpu_rating=random.uniform(1.0, 5.0), reputation_score=random.uniform(0.5, 1.0), ram_usage=random.uniform(100, 500), network=network))
    
    print(val_nodes)

    for val_node in val_nodes:
        network.add_validator_node(val_node)
        network.plot_shard_changes() 


if __name__ == '__main__':
    main()