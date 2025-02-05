class Network:
    def __init__(self):
        self.shards = []
        self.nodes = {}
        self.global_message_log = []
        self.global_requests = []
        self.current_primary_node = None
        self.commit_votes = {}
        self.completed_requests = set()

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
    
    def add_shard(self, shard):
        self.shards.append(shard)

    
    def find_shard_of_node(self, node_id): # Current lookup time, O(n^2), edit code later to ensure that lookup time is O(1) by adding nodes and shard to hashmap
        for shard in self.shards:
            for node in shard.validator_nodes + shard.client_nodes:
                if node.get_node_id() == node_id: # Check if the current node we find searching through the shards is equal to the node_id we are trying to find
                    return shard
    
