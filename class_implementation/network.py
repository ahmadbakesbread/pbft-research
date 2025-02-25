import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from clustering_model.shard_clustering import compute_subshards_ward
from shard import Shard
import matplotlib.pyplot as plt


class Network:
    def __init__(self, min_nodes_per_shard=3, max_nodes_per_shard=10):
        self.shards = {}
        self.min_nodes_per_shard = min_nodes_per_shard
        self.max_nodes_per_shard = max_nodes_per_shard
        self.validator_nodes = set()
        self.client_nodes = {}
        self.global_message_log = []
        self.global_requests = []
        self.current_primary_node = None
        self.commit_votes = {}
        self.completed_requests = set()
        self.prev_shard_assignments = None  # Track previous shard assignments


    def log_message(self, sender_id, receiver_id, message):
        """
        Log a message globally.
        """
        log_entry = {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "message": message,
            "timestamp": self.get_timestamp()
        }
        self.global_message_log.append(log_entry)
        print(f"LOGGED MESSAGE: {log_entry}")  # Debugging output

    def log_request(self, sender_id, request):
        """
        Log a request for the primary node to see.
        """
        log_entry = {
            "sender_id": sender_id,
            "request": request,
            "timestamp": self.get_timestamp()
        }

        self.global_requests.append(log_entry)


    def required_prepare_threshold(self):
        """ Return 2f+1 threshold for PBFT consensus. """
        f = (len(self.validator_nodes) - 1) // 3  # Maximum Byzantine nodes
        return 2 * f + 1
    
    def required_commit_threshold(self):
        """ Return 2f+1 threshold for COMMIT phase. """
        f = (len(self.validator_nodes) - 1) // 3
        return 2 * f + 1

    def broadcast(self, message, exclude=[]):
        for validator_node in self.validator_nodes:
            if validator_node not in exclude:
                if message["type"] == "PRE-PREPARE":
                    validator_node.receive_preprepare(message)
                elif message["type"] == "PREPARE":
                    validator_node.receive_prepare(message)
                elif message["type"] == "COMMIT":
                    validator_node.receive_commit(message)

    def get_global_message_log(self):
        """
        Retrieve the global message log.
        """
        return self.global_message_log

    def get_timestamp(self):
        """
        Generate a timestamp for message logging.
        """
        from datetime import datetime
        return datetime.now().isoformat()

    def get_replicas(self):
        '''Returns all replica nodes'''
        replicas = []

        for node in self.validator_nodes:
            if node != self.current_primary_node:
                replicas.append(node)
        
        return replicas
    
    def get_shards(self):
        return self.shards
    
    def get_requests(self):
        return self.global_requests
    
    def get_primary_node(self):
        return self.current_primary_node

    def change_view(self):
        pass

    def track_commit_vote(self, digest, node_id):
        """ Track that a node has received 2f+1 commits and is ready to finalize. """
        if digest not in self.commit_votes:
            self.commit_votes[digest] = set()

        self.commit_votes[digest].add(node_id)

        # 1️⃣ Check if at least 2f+1 nodes have confirmed 2f+1 commits
        if len(self.commit_votes[digest]) >= self.required_commit_threshold():
            self.confirm_client_request(digest)

    def confirm_client_request(self, digest):
        """ Finalize and execute the request only when 2f+1 nodes have received 2f+1 commits. """
        if digest in self.completed_requests:
            print(f"⚠️ Network: Request {digest[:8]} was already finalized.")
            return
        
        self.completed_requests.add(digest)
        print(f"✅✅ Network: Request {digest[:8]} has been finalized and executed!")

    def get_completed_requests(self):
        return self.completed_requests

    
    def add_shard(self, shard): # Old method of sharding within blockchain, no longer using this method.
        self.shards.append(shard)
    
    
    def find_shard_of_node(self, node_id): # Current lookup time, O(n^2), edit code later to ensure that lookup time is O(1) by adding nodes and shard to hashmap
        for shard in self.shards:
            for node in shard.validator_nodes + shard.client_nodes:
                if node.get_node_id() == node_id: # Check if the current node we find searching through the shards is equal to the node_id we are trying to find
                    return shard
    
    def recompute_shards(self):
        """ Recalculate shard assignments dynamically. """
        total_nodes = len(self.validator_nodes)

        if total_nodes == 0:
            print("⚠ No validator nodes available.")
            return None  

        if total_nodes < 2:
            print("⚠ Not enough nodes to perform clustering. Assigning all to one shard.")
            return {0: {"nodes": list(self.validator_nodes), "centroid": None}}  # Place all in one shard


        n_shards = max(1, total_nodes // self.max_nodes_per_shard)  # Prevent too many shards
        n_shards = min(n_shards, total_nodes // self.min_nodes_per_shard)  # Prevent too few shards

        if n_shards < 1:
            print("⚠ Not enough nodes to form shards. Assigning all to one shard.")
            n_shards = 1  # Ensure at least one shard exists
        
        print(f"🔄 Recomputing shards... Expected number of shards: {n_shards}")

        new_shards = compute_subshards_ward(self, n_shards)

        if new_shards is None:
            print("⚠ Failed to recompute shards.")
            return  

        # Reset current shards
        self.shards = {}
        self.shard_centroids = {}

        for shard_id, shard_info in new_shards.items():
            # Create new shard
            self.shards[shard_id] = Shard(shard_id=shard_id, network=self)

            # Assign nodes to this shard
            for node in shard_info["nodes"]:
                self.shards[shard_id].add_validator_node(node)
                node.shard = self.shards[shard_id]  # Update node's shard reference

            # Store centroid for future use
            self.shard_centroids[shard_id] = shard_info["centroid"]

        print(f"✅ Shards recomputed dynamically. Total shards: {len(self.shards)}")

    
    def add_validator_node(self, validator_node):
        self.validator_nodes.add(validator_node)
        self.recompute_shards()

    def plot_shard_changes(self):
        """ Plot movement of nodes between shards. """
        new_shard_assignments = {}
        for shard_id, shard in self.shards.items():
            for node in shard.validator_nodes:
                new_shard_assignments[node.node_id] = shard_id

        # 🟢 If no previous assignments exist, just store current state
        if self.prev_shard_assignments is None:
            self.prev_shard_assignments = new_shard_assignments.copy()
            print("⚠ First iteration - no previous shard assignments to compare.")
            return

        plt.figure(figsize=(10, 5))
        moved_nodes = False  # Check if any node moved

        for node_id, prev_shard in self.prev_shard_assignments.items():
            new_shard = new_shard_assignments.get(node_id, None)
            if new_shard is not None and prev_shard != new_shard:
                moved_nodes = True
                plt.scatter(node_id, prev_shard, color='red', label='Previous' if node_id == 0 else "")
                plt.scatter(node_id, new_shard, color='blue', label='New' if node_id == 0 else "")

        plt.xlabel("Node ID")
        plt.ylabel("Shard ID")
        plt.title("Node Movements Between Shards")
        if moved_nodes:
            plt.legend()
            plt.show()
        else:
            print("✅ No nodes moved between shards.")

        self.prev_shard_assignments = new_shard_assignments.copy()  # ✅ Update history
