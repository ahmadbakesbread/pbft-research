from network import Network
from validator_node import ValidatorNode
from client_node import ClientNode

def main():
    network = Network()

    client_node = ClientNode(node_id=1, network=network, shard_id=0, reputation_score=1.0)
    val_node1 = ValidatorNode(node_id=2, network=network, shard_id=0, reputation_score=1.0, isPrimary=True) # Primary Node
    val_node2 = ValidatorNode(node_id=3, network=network, shard_id=0, reputation_score=1.0)
    val_node3 = ValidatorNode(node_id=4, network=network, shard_id=0, reputation_score=1.0)
    val_node4 = ValidatorNode(node_id=5, network=network, shard_id=0, reputation_score=1.0)

    # Add nodes to the network
    network.add_client_node(client_node)
    network.add_validator_node(val_node1)
    network.add_validator_node(val_node2)
    network.add_validator_node(val_node3)
    network.add_validator_node(val_node4)


    client_node.create_request("Client has sent 5 supercoins.")

    print(f"All logged requests from Network's perspective: {network.get_requests()}") # Network object will now have the request logged.

    print(f"All logged requests from Node 1's perspective: {val_node1.check_requests()}") # Primary validator node will be authorized to check requests.

    client_requests = val_node1.check_requests()

    val_node1.handle_request(client_requests[0])

    for val_node in network.get_replicas():
        val_node.process_prepare() # Process Prepare is both responsible for the process method and commit method, if you check the process prepare method it then jumps to commit method, almost happening as if it were 2 stages.

    print(network.get_completed_requests()) # Will show that network has completed the request

    print(network.confirm_client_request('385489726cdedafa30a8b63954eec8e7e0f9544de58d5dce39018cf162c06481'))





if __name__ == "__main__":
    main()