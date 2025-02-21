from base_node import Node
from abc import abstractmethod
from network import Network
from shard import Shard
import hashlib
import json

class ValidatorNode(Node):

    def __init__(self, node_id, network, shard=None, reputation_score=1.0, cpu_rating = 1.0, ram_usage = 1.0, isPrimary=False, name=None):
        super().__init__(node_id, role="validator", network=network, shard=shard, name=name)
        self.reputation_score = reputation_score
        self.cpu_rating = cpu_rating
        self.ram_usage = ram_usage
        self.isPrimary = isPrimary  
        self.pending_prepares = []
        self.pending_commits = {}
        self.commit_votes = {}

    
    def get_cpu_rating(self):
        return self.cpu_rating
    
    def get_reputation_score(self):
        return self.reputation_score
    

    def decide_shard(self):
        pass # This method requires the ML model to be complete, will complete soon however.

    def check_requests(self):
        if not self.isPrimary:
            print("Only primary node is authorized to check requests")
            return

        requests = self.shard.get_requests()

        return requests

    def handle_request(self, message):
        """ Primary node handles a client request and sends PRE-PREPARE to replicas. """
        if not self.isPrimary:
            print("Only primary node is authorized to check requests")
            return
        
        digest = hashlib.sha256(json.dumps(message).encode()).hexdigest()
        
        pre_prepare_msg = {
        "type": "PRE-PREPARE",
        "digest": digest,
        "primary_id": self.node_id,
        "client_request": message  
        }


        self.shard.broadcast(pre_prepare_msg, exclude=[self])  # Exclude self

    def receive_preprepare(self, pre_prepare_msg):
        """ Replicas receive PRE-PREPARE and store it for processing. """
        digest = hashlib.sha256(json.dumps(pre_prepare_msg["client_request"]).encode()).hexdigest()
        
        if digest != pre_prepare_msg["digest"]:
            print(f"Node {self.node_id}: Invalid digest in PRE-PREPARE, rejecting message.")
            return

        print(f"Node {self.node_id}: Received PRE-PREPARE for request {digest[:8]} from primary node, node_id: {pre_prepare_msg['primary_id']}.")

        self.pending_prepares.append(pre_prepare_msg)
    
    def process_prepare(self):
        """ Process stored PRE-PREPARE messages and move to PREPARE phase. """
        for pre_prepare_msg in self.pending_prepares:
            digest = pre_prepare_msg["digest"]

            print(f"🟡 Node {self.node_id}: Processing PRE-PREPARE -> Sending PREPARE.")

            # Create and send PREPARE message
            prepare_msg = {
                "type": "PREPARE",
                "digest": digest,
                "validator_id": self.node_id
            }
            self.shard.broadcast(prepare_msg)

        # Clear processed messages
        self.pending_prepares.clear()


    def receive_prepare(self, prepare_msg):
        digest = prepare_msg["digest"]
        if digest not in self.pending_commits:
            self.pending_commits[digest] = set()

        self.pending_commits[digest].add(prepare_msg["validator_id"])

        if digest not in self.pending_commits:
            self.pending_commits[digest] = set()

        self.pending_commits[digest].add(prepare_msg["validator_id"])

        if len(self.pending_commits[digest]) >= self.shard.required_prepare_threshold():
            print(f"🟢 Node {self.node_id}: Reached 2f+1 PREPAREs -> Sending COMMIT.")

        commit_msg = {
            "type": "COMMIT",
            "digest": digest,
            "validator_id": self.node_id
        }

        self.shard.broadcast(commit_msg)


    def receive_commit(self, commit_msg):
        """ Process incoming COMMIT messages and notify the shard when consensus is reached. """
        digest = commit_msg["digest"]

        # 1️⃣ Track received COMMIT messages
        if digest not in self.commit_votes:
            self.commit_votes[digest] = set()

        self.commit_votes[digest].add(commit_msg["validator_id"])

        print(f"🔵 Node {self.node_id}: Received COMMIT for {digest[:8]} from {commit_msg['validator_id']}.")

        # 2️⃣ If we have 2f+1 COMMIT messages, notify the network to finalize the request
        if len(self.commit_votes[digest]) >= self.shard.required_commit_threshold():
            self.shard.track_commit_vote(digest, self.node_id)  # 🏁 The network handles finalization