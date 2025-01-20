from flask import Flask, request, jsonify
import requests
import hashlib
import json
import sys
import random
app = Flask(__name__)

all_nodes = ["http://localhost:5000", "http://localhost:5001", "http://localhost:5002", "http://localhost:5003"]
max_faulty_nodes = (len(all_nodes) - 1) // 3
port = int(sys.argv[1])  
self_node_url = f"http://localhost:{port}"

view_no = 0 # Initial Primary Node

byzantine_nodes = set()  # Stores node in set if it is detected as a faulty node
byzantine_node = None # Randomly select byzantine node

primary_timeout = 5  # The max timeout for primary node to be detected as a failure node 

prepare_messages = {}  # Tracks prepare messages by sender
digest_counts = {}


def get_primary():
    ''''Returns primary node'''
    return all_nodes[view_no % len(all_nodes)]

def get_replicas():
    '''Returns all replica nodes'''
    replicas = []

    for node in all_nodes:
        if node != self_node_url:
            replicas.append(node)
    
    return replicas

def select_byzantine_node():
    """Randomly selects a Byzantine node from the replicas (not the primary)."""
    global byzantine_node
    replicas = get_replicas()

    if replicas:
        byzantine_node = random.choice(replicas)
        print(f"⚠️ Byzantine node selected: {byzantine_node}")

@app.route('/change-view', methods=['POST'])
def change_view():
    global view_no
    view_no += 1

    print(f"View change initiated! New primary: {get_primary()}")

    return jsonify({"status": "NEW_PRIMARY", "primary": get_primary()})


@app.route('/request', methods=['POST'])
def handle_request():

    primary = get_primary()
    if self_node_url != primary:
        return jsonify({"error": "Only the primary node can accept client requests"}), 403

    # If the current primary is a known Byzantine node, trigger view change
    if primary in byzantine_nodes:
        print(f"⚠️ Primary node {primary} is Byzantine! Triggering view change...")
        requests.post(f"{self_node_url}/change-view")  # Trigger view change

        return jsonify({"error": "Primary node is Byzantine. View change initiated."}), 503



    data = request.json
    digest = hashlib.sha256(json.dumps(data).encode()).hexdigest()
    message = {"type": "PRE-PREPARE", "digest": digest}


    replicas = get_replicas()
    # Broadcast pre-prepare to other nodes
    for node in replicas:
        requests.post(f"{node}/preprepare", json=message)

    return jsonify({"status": "OK", "digest": digest})


@app.route('/preprepare', methods=['POST'])
def handle_preprepare():
    data = request.json
    sender = data.get("sender")

    # If the sender is already known to be Byzantine, reject immediately
    if sender in byzantine_nodes:
        return jsonify({"status": "REJECTED", "reason": "Sender is a known Byzantine node"}), 400
    
    # If this node is the selected Byzantine node, send a bad digest
    if self_node_url == byzantine_node:
        bad_digest = hashlib.sha256(b"ByzantineAttack").hexdigest()
        message = {"type": "PREPARE", "digest": bad_digest, "sender": self_node_url}
        print(f"⚠️ Malicious Node {self_node_url} sending faulty digest!")
    else:
        message = {"type": "PREPARE", "digest": data["digest"], "sender": self_node_url}


    replicas = get_replicas()

    # Broadcast prepare to other nodes
    for node in replicas:
        requests.post(f"{node}/prepare", json=message)

    return jsonify({"status": "OK"})



@app.route('/prepare', methods=['POST'])
def handle_prepare():
    data = request.json
    
    sender = data["sender"]
    digest = data["digest"]

    # If the sender is a known Byzantine node, reject immediately
    if sender in byzantine_nodes:
        return jsonify({"status": "REJECTED", "reason": "Sender is a known Byzantine node"}), 400
    
    # Check if the digest is new or conflicting
    if sender not in prepare_messages:
        prepare_messages[sender] = digest  # Store the first digest from this sender

        # Track how many nodes report this digest
        if digest not in digest_counts:
            digest_counts[digest] = 1
        else:
            digest_counts[digest] += 1

        # Byzantine check: If a different digest is more common, flag the sender
        majority_digest = max(digest_counts, key=digest_counts.get)  # Find most common digest
        if digest_counts[majority_digest] >= 2:  # Ensure there's majority agreement
            if digest != majority_digest:
                print(f"⚠️ Byzantine node detected! {sender} sent an uncommon digest.")
                byzantine_nodes.add(sender)
                return jsonify({"status": "REJECTED", "reason": "Conflicting messages detected"}), 400

    elif prepare_messages[sender] != digest:  # If the sender sends a different digest later, flag it
        print(f"⚠️ Byzantine node detected! {sender} sent conflicting messages.")
        byzantine_nodes.add(sender)
        return jsonify({"status": "REJECTED", "reason": "Conflicting messages detected"}), 400

   
    # If we receive 2f + 1 valid prepare messages, broadcast commit
    message = {"type": "COMMIT", "digest": digest, "sender": self_node_url}
    for node in all_nodes:
        if node != self_node_url:
            requests.post(f"{node}/commit", json=message)

    return jsonify({"status": "OK"})


@app.route('/commit', methods=['POST'])
def handle_commit():
    data = request.json
    print(f"Committed: {data['digest']}")

    # Send REPLY back to the client
    client_url = data.get("client_url", "http://localhost:5004")  # Default client URL
    reply_message = {"type": "REPLY", "digest": data["digest"], "status": "COMMITTED"}
    requests.post(f"{client_url}/reply", json=reply_message)

    return jsonify({"status": "COMMITTED", "digest": data["digest"]})



if __name__ == "__main__":
    app.run(port=port)
