import requests
import hashlib
import json

client_url = "http://localhost:5004"  # Client URL
primary_node = "http://localhost:5000"

def send_request(data):
    """Send request to primary node."""
    digest = hashlib.sha256(json.dumps(data).encode()).hexdigest()
    request_data = {"operation": data, "client_url": client_url}

    response = requests.post(f"{primary_node}/request", json=request_data)
    print(f"Sent request: {response.json()}")

if __name__ == "__main__":
    send_request({"operation": "transfer", "amount": 100})
