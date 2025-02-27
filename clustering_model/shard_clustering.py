import numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans
import random
from dummy_network import DummyNetwork, DummyNode 

def compute_shard_centroid(shard_centroid):
    if not shard_centroid:
        return None  # No subshards

    return np.mean(shard_centroid, axis=0)  # Average centroid of all subshards

    

def compute_subshards_ward(network, n_shards):
    """ Perform Ward hierarchical clustering on a network to divide it into shards. """

    total_nodes = len(network.validator_nodes)

    if total_nodes == 0:
        print("No validator nodes available.")
        return None  


    feature_matrix = []

    for node in network.validator_nodes:
        feature_matrix.append([node.cpu_rating, node.reputation_score, node.ram_usage])

    feature_matrix = np.array(feature_matrix)

    if len(feature_matrix) < n_shards:
        print("Not enough nodes to form clusters")
        return None  # Not enough nodes to form clusters
    

    clustering = AgglomerativeClustering(
        n_clusters=n_shards,
        metric='euclidean',
        linkage='ward'  
    )

    labels = clustering.fit_predict(feature_matrix)

    # Group nodes by their cluster label
    subshards = {}
    for i, node in enumerate(network.validator_nodes):
        label = labels[i]
        if label not in subshards:
            subshards[label] = []
        subshards[label].append(node) 

    # Compute centroid for each subshard, each centorid contains the cpu_rating, reputation_score, and ram_usage of the shard.
    result = {}
    features = []
    for label, nodes in subshards.items():
        features = np.array([
            [node.cpu_rating, node.reputation_score, node.ram_usage] for node in nodes
        ])
        centroid_vector = features.mean(axis=0)
        result[label] = {"nodes": nodes, "centroid": centroid_vector}

    return result


if __name__ == '__main__':
    nodes = [
    DummyNode(node_id=i, 
             cpu_rating=random.uniform(1.0, 5.0), 
             reputation_score=random.uniform(0.5, 1.0), 
             ram_usage=random.uniform(100, 500))
    for i in range(20)
    ]


    network = DummyNetwork(nodes)

    n_shards = 3

    subshards = compute_subshards_ward(network, n_shards)

    for shard_id, shard_info in subshards.items():
        print(f"Shard {shard_id}: Centroid -> {shard_info['centroid']}")
        print(f"Shard {shard_id}: Nodes -> {[node for node in shard_info['nodes']]}")
        print("=" * 50)
