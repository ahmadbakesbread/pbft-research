class Network:
    def __init__(self):
        self.nodes = []
        self.global_message_log = []

    def add_node(self, node):
        """
        Add a node to the network.
        """
        self.nodes.append(node)

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
