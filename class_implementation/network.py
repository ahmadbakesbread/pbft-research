from math import comb
import sys
import os

from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabasz_score

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from shard import Shard
import matplotlib.pyplot as plt
import numpy as np
import random

class Network:
    def __init__(self, s_min=3, s_max=20, lambda_val=0.4, byzantine_threshold=0.3):
        self.shards = {}
        self.shard_centroids = {}
        self.validator_nodes = set()
        self.client_nodes = {}
        self.global_message_log = []
        self.global_requests = []
        self.current_primary_node = None
        self.commit_votes = {}
        self.completed_requests = set()
        self.prev_shard_assignments = None  # Track previous shard assignments

        # Parameters for optimal sharding
        self.s_min = s_min
        self.s_max = s_max
        self.lambda_val = lambda_val
        self.byzantine_threshold = byzantine_threshold

        self.N = len(self.validator_nodes)
        self.K_malicious = int(self.N * 0.2)



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
            print("No validator nodes available.")
            return

        # Extract feature matrix; here we use CPU rating and RAM usage (you can add more features if desired)
        X = np.array([[node.cpu_rating, node.ram_usage] for node in self.validator_nodes])
        
        s_values = np.arange(self.s_min, self.s_max + 1)
        ch_scores = []
        penalized_scores = []

        best_kmeans = None
        best_labels = None

        # Iterate over candidate shard counts
        for s in s_values:
            # Apply K-Means clustering with s clusters
            kmeans = KMeans(n_clusters=s, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)

            # Compute the Calinski-Harabasz index (negated so lower is better)
            ch_index = -calinski_harabasz_score(X, labels) if s > 1 else 0
            ch_scores.append(ch_index)

            # Compute Byzantine risk probability for shard size = ceil(total_nodes / s)
            n_shard_size = int(np.ceil(total_nodes / s))
            threshold = int(np.ceil(n_shard_size * self.byzantine_threshold))
            hypergeom_tail = 0
            denom = comb(total_nodes, n_shard_size)
            for k in range(threshold, n_shard_size + 1):
                hypergeom_tail += comb(self.K_malicious, k) * comb(total_nodes - self.K_malicious, n_shard_size - k)
            byzantine_risk = hypergeom_tail / denom

            penalty = self.lambda_val * byzantine_risk * (s - self.s_min) ** 2
            penalized_score = ch_index + penalty
            penalized_scores.append(penalized_score)

            # Store best solution based on the combined objective
            if s == s_values[np.argmin(penalized_scores)]:
                best_kmeans = kmeans
                best_labels = labels

        opt_s = s_values[np.argmin(penalized_scores)]
        print(f"Optimal number of shards (with penalty): {opt_s}")

        # Now assign nodes to shards using the best clustering solution
        new_shards = {}  # shard_id -> list of nodes
        for i, node in enumerate(self.validator_nodes):
            label = best_labels[i]
            if label not in new_shards:
                new_shards[label] = []
            new_shards[label].append(node)

        # Update network's shard assignments and compute centroids
        self.shards = new_shards
        self.shard_centroids = {}
        for label, nodes in self.shards.items():
            features = np.array([[node.cpu_rating, node.ram_usage] for node in nodes])
            self.shard_centroids[label] = features.mean(axis=0)
            # Optionally, you can update a node's shard attribute if defined:
            for node in nodes:
                node.shard = label

        print(f"Shards recomputed dynamically. Total shards: {len(self.shards)}")


    
    def add_validator_node(self, validator_node):
        self.validator_nodes.update(validator_node)
        self.recompute_shards()
        self.N = len(self.validator_nodes)
        self.K_malicious = int(self.N * 0.2)
        self.recompute_shards()

