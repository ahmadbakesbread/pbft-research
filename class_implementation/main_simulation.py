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

    shard_0 = net.shards.get(0)
    shard_1 = net.shards.get(1)


    print(f"Shard 0: {shard_0}")
    print(f"Shard 1: {shard_1}")

    print(f"Shard 0 Primary Node: {shard_0.get_primary_node()}") 

    print(f"Shard 1 Primary Node: {shard_1.get_primary_node()}") 

    client_0 = random.choice(list(shard_0.client_nodes.values()))
    client_1 = random.choice(list(shard_1.client_nodes.values()))
    primary_1 = shard_1.get_primary_node()

    client_0.create_request("Ahmad has sent 5 supercoins to Naseem.", client_1.get_node_id())

    print(f"All logged requests from Shard 1's perspective: {shard_0.get_requests()}") # Should be empty
    
    print(f"All logged requests from Shard 2's perspective: {shard_1.get_requests()}") # Shard object will now have the request logged.

    print(f"All logged requests from Validator Node 5's perspective: {primary_1.check_requests()}") # Primary validator node will be authorized to check requests.

    client_requests = primary_1.check_requests()

    primary_1.handle_request(client_requests[0])

    for val_node in shard_1.get_replicas():
        val_node.process_prepare() # Process Prepare is both responsible for the process method and commit method, if you check the process prepare method it then jumps to commit method, almost happening as if it were 2 stages.

    print(shard_1.get_completed_requests()) # Will show that network has completed the request










if __name__ == '__main__':
    main()
