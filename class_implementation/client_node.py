from base_node import Node
from network import Network
import sys
import hashlib
import json

class ClientNode(Node):
        """
        Initialize a client node.

        :param node_id: Unique identifier for the node.
        :param shard_id: The shard the node is currently part of (if any).
        :param reputation_score: A score representing the node's trustworthiness (default: 1.0).
        :param ram_usage: Current RAM usage of the node (default: 0.0).
        """

        def __init__(self, node_id, network, shard_id=None, reputation_score=1.0):
            super().__init__(node_id, network=network, role="client", shard_id=shard_id)
            self.reputation_score = reputation_score

        def receive_message(self, message):
            """
            Receive a message and add it to the message queue.
            """
            self.message_queue.append(message)
            print(f"Client Node {self.node_id} received message: {message}")

        def create_request(self, data):
            request = {
            "operation": data,
            "client_node_id": self.node_id
            }

            self.network.log_request(self.node_id, request)


        
        def decide_shard(self, shard_loads):
            """
            Decide which shard to join based on shard loads and the node's own state.
            Client nodes typically do not decide their shard; they are assigned one.
            """
            print(f"Client Node {self.node_id} does not decide its shard.")
            return self.shard_id

def main():
    network_obj = Network()
    client_node1 = ClientNode(node_id=1, network=network_obj, shard_id=0, reputation_score=0.9)
    client_node2 = ClientNode(node_id=2, network=network_obj, shard_id=0, reputation_score=0.9)

    network_obj.add_node(client_node1)
    network_obj.add_node(client_node2)

    client_node1.send_message("Hello, Node 2!", receiver_id=2)

    print("Global Log:", network_obj.get_global_message_log())

    client_node1.create_request("Ahmad sent 5 btc")

    print(network_obj.get_requests())


if __name__ == '__main__':
     main()