from abc import ABC, abstractmethod

class Node(ABC):
    def __init__(self, node_id, role, shard_id=None):
        """
        Initialize a node in the PBFT network.

        :param node_id: Unique identifier for the node.
        :param role: Role of the node (e.g., "client", "validator").
        :param shard_id: The shard the node is currently part of (if any).
        :param reputation_score: A score representing the node's trustworthiness (default: 1.0).
        :param ram_usage: Current RAM usage of the node (default: 0.0).
        """
        self.node_id = node_id
        self.role = role
        self.shard_id = shard_id
        self.message_queue = []  # Queue for incoming messages

    @abstractmethod
    def send_message(self, message, receiver_id=None):
        """
        Send a message to another node or broadcast it to the network.
        Must be implemented by derived classes.
        """
        pass

    @abstractmethod
    def receive_message(self, message):
        """
        Receive a message and add it to the message queue.
        Must be implemented by derived classes.
        """
        pass

    @abstractmethod
    def decide_shard(self, shard_loads):
        """
        Decide which shard to join based on shard loads and the node's own state.
        Must be implemented by derived classes.
        """
        pass

    def __str__(self):
        """
        String representation of the node.
        """
        return (f"Node(ID={self.node_id}, Role={self.role}, Shard={self.shard_id}, "
                f"Reputation={self.reputation_score}, RAM Usage={self.ram_usage})")