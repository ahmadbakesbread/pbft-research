from flask import Flask, request, jsonify

app = Flask(__name__)

replies_received = {}

@app.route('/reply', methods=['POST'])
def handle_reply():
    """Handle reply messages from nodes."""
    data = request.json
    digest = data["digest"]

    if digest not in replies_received:
        replies_received[digest] = []
    replies_received[digest].append(data)

    print(f"Received reply: {data}")

    # If we received at least 2 replies (f+1), finalize confirmation
    if len(replies_received[digest]) >= 2:
        print(f"✅ Request {digest} finalized by PBFT!")

    return jsonify({"status": "RECEIVED", "digest": digest})

if __name__ == "__main__":
    print("Client listening for replies at http://localhost:5004")
    app.run(port=5004)
