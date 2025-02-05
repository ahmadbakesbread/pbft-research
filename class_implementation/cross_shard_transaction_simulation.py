from network import Network
from validator_node import ValidatorNode
from client_node import ClientNode
from shard import Shard

def main():
    network = Network()
    shard1 = Shard(shard_id=1, network=network)
    shard2 = Shard(shard_id=2, network=network)
    network.add_shard(shard1)
    network.add_shard(shard2)

    # Shard 1 Nodes:
    client_node1 = ClientNode(node_id=1, network=network, shard=shard1, reputation_score=1.0)
    val_node1 = ValidatorNode(node_id=2, network=network, shard=shard1, reputation_score=1.0, isPrimary=True) # Primary Node
    val_node2 = ValidatorNode(node_id=3, network=network, shard=shard1, reputation_score=1.0)
    val_node3 = ValidatorNode(node_id=4, network=network, shard=shard1, reputation_score=1.0)
    val_node4 = ValidatorNode(node_id=5, network=network, shard=shard1, reputation_score=1.0)

    # Shard 2 Nodes:
    client_node2 = ClientNode(node_id=6, network=network, shard=shard2, reputation_score=1.0)
    val_node5 = ValidatorNode(node_id=7, network=network, shard=shard2, reputation_score=1.0, isPrimary=True) # Primary Node
    val_node6 = ValidatorNode(node_id=8, network=network, shard=shard2, reputation_score=1.0)
    val_node7 = ValidatorNode(node_id=9, network=network, shard=shard2, reputation_score=1.0)
    val_node8 = ValidatorNode(node_id=10, network=network, shard=shard2, reputation_score=1.0)



    # Add nodes to the shard
    shard1.add_client_node(client_node1)
    shard1.add_validator_node(val_node1)
    shard1.add_validator_node(val_node2)
    shard1.add_validator_node(val_node3)
    shard1.add_validator_node(val_node4)

    shard2.add_client_node(client_node2)
    shard2.add_validator_node(val_node5)
    shard2.add_validator_node(val_node6)
    shard2.add_validator_node(val_node7)
    shard2.add_validator_node(val_node8)


    

    client_node1.create_request("Ahmad has sent 5 supercoins to Naseem.", client_node2.get_node_id())

    print(f"All logged requests from Shard 1's perspective: {shard1.get_requests()}") # Should be empty
    
    print(f"All logged requests from Shard 2's perspective: {shard2.get_requests()}") # Shard object will now have the request logged.

    print(f"All logged requests from Validator Node 5's perspective: {val_node5.check_requests()}") # Primary validator node will be authorized to check requests.

    client_requests = val_node5.check_requests()

    val_node5.handle_request(client_requests[0])

    for val_node in shard2.get_replicas():
        val_node.process_prepare() # Process Prepare is both responsible for the process method and commit method, if you check the process prepare method it then jumps to commit method, almost happening as if it were 2 stages.

    print(shard2.get_completed_requests()) # Will show that network has completed the request

    print(shard2.confirm_client_request('5b143a05c1510cc69ee81be98153edf8cc99cf5d76cf4038b1275601f98b3f14'))





if __name__ == "__main__":
    main()