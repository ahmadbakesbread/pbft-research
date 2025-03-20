import numpy as np

class Shard:
    def __init__(self, shard_id, network):
        self.client_nodes = {}
        self.validator_nodes = []
        self.global_message_log = []
        self.shard_requests = []
        self.current_primary_node = None
        self.commit_votes = {}
        self.network = network
        self.completed_requests = set()
        self.shard_id = shard_id
        self.global_requests = []
        self.centroid = self.compute_centroid()


    def get_shard_id(self):
        return self.shard_id
    
    def add_client_node(self, client_node):
        """
        Add a node to the network.
        """

        self.client_nodes[client_node.node_id] = client_node  # Store by node_id as the key
        client_node.shard = self  # Assign shard to the client

    
    def add_validator_node(self, validator_node):
        self.validator_nodes.append(validator_node)

        # If no primary exists, set the first node as primary
        if not self.current_primary_node:
            self.current_primary_node = validator_node
            validator_node.isPrimary = True

        validator_node.shard = self
        
    def add_log_request(self, log_entry):
        self.global_requests.append(log_entry)


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

    def log_request(self, sender_id, receiver_id, request):
        """
        Log a request for the primary node to see.
        """
        log_entry = {
            "sender": sender_id,
            "receiver": receiver_id,
            "request": request,
            "timestamp": self.get_timestamp()
        }

        sender_shard = self.network.find_shard_of_node(sender_id)
        receiver_shard = self.network.find_shard_of_node(receiver_id)

        if sender_shard == receiver_shard:
            print("Both Sender and Receiver Client Nodes are in the same shard")
            self.add_log_request(log_entry)
        elif sender_shard != receiver_shard:
            print(" Sender and Receiver Client Nodes are not in the same shard, sending request over to receiver shard.")
            receiver_shard.add_log_request(log_entry)
        else:
            print("Either sender or receiver Client Nodes are invalid.")        

        

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
    
    def compute_centroid(self):
        """Compute the centroid based on node features."""
        if not self.validator_nodes:
            return None
        features = np.array([[node.cpu_rating, node.ram_usage] for node in self.validator_nodes])
        return features.mean(axis=0)

    
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


    def __repr__(self):
        return f"Shard(id={self.shard_id}, val_nodes={self.validator_nodes}, client_nodes={self.client_nodes})"