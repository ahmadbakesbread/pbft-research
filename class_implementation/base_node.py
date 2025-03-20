from abc import ABC, abstractmethod
from network import Network
from shard import Shard

class Node(ABC):
    def __init__(self, node_id, name, role, network, shard=None):
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
        self.name = name
        self.network = network
        self.shard = shard
        self.message_log = []  # Queue for incoming messages

    def send_message(self, message, receiver_id=None):
        """
        Send a message to a specific node or broadcast it.
        """
        if receiver_id is not None:
            print(f"Node {self.node_id} sending message to Node {receiver_id}: {message}")
            self.shard.log_message(self.node_id, receiver_id, message)
        else:
            print(f"Node {self.node_id} broadcasting message: {message}")
            for node in self.shard.nodes:
                if node.node_id != self.node_id:
                    self.shard.log_message(self.node_id, node.node_id, message)

    @abstractmethod
    def decide_shard(self, shard_loads):
        """
        Decide which shard to join based on shard loads and the node's own state.
        Must be implemented by derived classes.
        """
        pass

    def check_message_log(self, filter_func=None):
        """
        Inspect the message log for specific messages or patterns.
        
        :param filter_func: A function to filter messages (e.g., by sender, content, or type).
        :param global_log: If True, retrieves messages from the global network log instead of the node's local log.
        :return: A list of messages that match the filter criteria.
        """
        
        log = self.network.get_global_message_log()

        if filter_func is None:
            return log
        else:
            return [msg for msg in log if filter_func(msg)]
    
    def get_node_id(self):
        return self.node_id
    
    def get_shard(self):
        return self.shard


    def __str__(self):
        """
        String representation of the node.
        """
        return (f"Node(ID={self.node_id}, Role={self.role})")
    
    def __repr__(self):
        return f"Node(id={self.node_id}, name={self.name})"
