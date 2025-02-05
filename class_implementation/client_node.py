from base_node import Node
from network import Network
from shard import Shard
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

        def __init__(self, node_id, network, shard=None, reputation_score=1.0):
            super().__init__(node_id, network=network, role="client", shard=shard)
            self.reputation_score = reputation_score

        def receive_message(self, message):
            """
            Receive a message and add it to the message queue.
            """
            self.message_queue.append(message)
            print(f"Client Node {self.node_id} received message: {message}")

        def create_request(self, data, receiver_id):
            transaction = {
            "operation": data,
            "client_node_id": self.node_id,
            "receiver": receiver_id
            }

            digest = hashlib.sha256(json.dumps(transaction).encode()).hexdigest()

            request = {
                "digest": digest,
                "transaction": transaction
            }

            self.shard.log_request(self.node_id, receiver_id, request)
        
        def decide_shard(self, shard_loads):
            """
            Decide which shard to join based on shard loads and the node's own state.
            Client nodes typically do not decide their shard; they are assigned one.
            """
            print(f"Client Node {self.node_id} does not decide its shard.")
            return self.shard_id

def main():
    network_obj = Network()
    shard = Shard()
    client_node1 = ClientNode(node_id=1, network=network_obj, shard=shard, reputation_score=0.9)
    client_node2 = ClientNode(node_id=2, network=network_obj, shard=shard, reputation_score=0.9)

    network_obj.add_shard(shard)

    shard.add_client_node(client_node1)
    shard.add_client_node(client_node2)

    client_node1.send_message("Hello, Node 2!", receiver_id=2)

    print("Global Log:", shard.get_global_message_log())

    client_node1.create_request("Ahmad sent 5 btc")

    print(f"All Shard's Requests: {shard.get_requests()}")


if __name__ == '__main__':
     main()