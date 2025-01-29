from class_implementation.base_node import Node

class ClientNode(Node):
        """
        Initialize a client node.

        :param node_id: Unique identifier for the node.
        :param shard_id: The shard the node is currently part of (if any).
        :param reputation_score: A score representing the node's trustworthiness (default: 1.0).
        :param ram_usage: Current RAM usage of the node (default: 0.0).
        """

        def __init__(self, node_id, shard_id=None, reputation_score=1.0, ram_usage=0.0):
            super().__init__(node_id, role="client", shard_id=shard_id)
            self.reputation_score = reputation_score
            self.ram_usage = ram_usage
    

        def send_message(self, message, receiver_id=None):
            """
            Sends a message to primary node.
            """
            if receiver_id is not None:
                print(f"Client Node {self.node_id} sending message to Node {receiver_id}: {message}")
            else:
                print(f"Client Node {self.node_id} broadcasting message: {message}")

        def receive_message(self, message):
            """
            Receive a message and add it to the message queue.
            """
            self.message_queue.append(message)
            print(f"Client Node {self.node_id} received message: {message}")

        
        def decide_shard(self, shard_loads):
            """
            Decide which shard to join based on shard loads and the node's own state.
            Client nodes typically do not decide their shard; they are assigned one.
            """
            print(f"Client Node {self.node_id} does not decide its shard.")
            return self.shard_id

