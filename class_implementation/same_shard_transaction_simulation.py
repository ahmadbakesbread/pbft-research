from network import Network
from validator_node import ValidatorNode
from client_node import ClientNode
from shard import Shard

def main():
    network = Network()
    shard = Shard(shard_id=1, network=network)
    network.add_shard(shard)

    client_node1 = ClientNode(node_id=1, network=network, shard=shard, reputation_score=1.0)
    client_node2 = ClientNode(node_id=1, network=network, shard=shard, reputation_score=1.0)
    val_node1 = ValidatorNode(node_id=2, network=network, shard=shard, reputation_score=1.0, isPrimary=True) # Primary Node
    val_node2 = ValidatorNode(node_id=3, network=network, shard=shard, reputation_score=1.0)
    val_node3 = ValidatorNode(node_id=4, network=network, shard=shard, reputation_score=1.0)
    val_node4 = ValidatorNode(node_id=5, network=network, shard=shard, reputation_score=1.0)


    # Add nodes to the shard
    shard.add_client_node(client_node1)
    shard.add_client_node(client_node2)
    shard.add_validator_node(val_node1)
    shard.add_validator_node(val_node2)
    shard.add_validator_node(val_node3)
    shard.add_validator_node(val_node4)
    

    client_node1.create_request("Ahmad has sent 5 supercoins to Naseem.", client_node2.get_node_id())

    print(f"All logged requests from Network's perspective: {shard.get_requests()}") # Shard object will now have the request logged.

    print(f"All logged requests from Validator Node 1's perspective: {val_node1.check_requests()}") # Primary validator node will be authorized to check requests.

    client_requests = val_node1.check_requests()

    val_node1.handle_request(client_requests[0])

    for val_node in shard.get_replicas():
        val_node.process_prepare() # Process Prepare is both responsible for the process method and commit method, if you check the process prepare method it then jumps to commit method, almost happening as if it were 2 stages.

    print(shard.get_completed_requests()) # Will show that network has completed the request

    print(shard.confirm_client_request('e18c3907ca0eea8c89118c116c4576181bafc2276bc53b97368a015a3aca3915'))


if __name__ == "__main__":
    main()