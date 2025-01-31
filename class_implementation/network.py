class Network:
    def __init__(self):
        self.client_nodes = []
        self.validator_nodes = []
        self.global_message_log = []
        self.global_requests = []
        self.current_primary_node = None


    def add_client_node(self, client_node):
        """
        Add a node to the network.
        """
        self.client_nodes.append(client_node)
    
    def add_validator_node(self, validator_node):
        self.validator_nodes.append(validator_node)

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
