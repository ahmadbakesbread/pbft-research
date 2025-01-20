from flask import Flask, request, jsonify
import requests
import hashlib
import json
import sys
app = Flask(__name__)

consensus_nodes = ["http://localhost:5001", "http://localhost:5002", "http://localhost:5003"]
primary_node = "http://localhost:5000"


@app.route('/request', methods=['POST'])
def handle_request():
    data = request.json
    digest = hashlib.sha256(json.dumps(data).encode()).hexdigest()
    message = {"type": "PRE-PREPARE", "digest": digest}

    # Broadcast pre-prepare to other nodes
    for node in consensus_nodes:
        requests.post(f"{node}/preprepare", json=message)

    return jsonify({"status": "OK", "digest": digest})


@app.route('/preprepare', methods=['POST'])
def handle_preprepare():
    data = request.json
    message = {"type": "PREPARE", "digest": data["digest"]}

    # Broadcast prepare to other nodes
    for node in consensus_nodes:
        requests.post(f"{node}/prepare", json=message)

    return jsonify({"status": "OK"})



@app.route('/prepare', methods=['POST'])
def handle_prepare():
    data = request.json
    message = {"type": "COMMIT", "digest": data["digest"]}

    # Broadcast commit to other nodes
    for node in consensus_nodes:
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
    port = int(sys.argv[1])  # Get port from command line
    app.run(port=port)
