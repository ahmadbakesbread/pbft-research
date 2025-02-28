import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
import random
from dummy_network import DummyNetwork, DummyNode 


def find_optimal_eps(X, min_pts):

    neigh = NearestNeighbors(n_neighbors=min_pts)
    neigh.fit(X)
    distances, _ = neigh.kneighbors(X)

    # Sort the k-th nearest neighbor distances
    distances = np.sort(distances[:, min_pts-1])

    elbow_index = np.argmax(np.diff(distances))  # Find max curvature change
    optimal_eps = distances[elbow_index]
    print(optimal_eps)
    return optimal_eps


def compute_subshards_dbscan(network, min_samples=2):
    """ Perform DBSCAN clustering on the network to divide it into shards. """
    
    total_nodes = len(network.validator_nodes)
    if total_nodes == 0:
        print("No validator nodes available.")
        return None  

    # Extract features from nodes
    feature_matrix = np.array([
        [node.cpu_rating, node.reputation_score, node.ram_usage] 
        for node in network.validator_nodes
    ])

    eps = find_optimal_eps(feature_matrix, min_samples)

    # Apply DBSCAN clustering
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean')
    labels = clustering.fit_predict(feature_matrix)

    # Group nodes by cluster labels
    subshards = {}
    outliers = []
    for i, node in enumerate(network.validator_nodes):
        label = labels[i]
        if label == -1:
            outliers.append(node)  # Nodes labeled as -1 are outliers
        else:
            if label not in subshards:
                subshards[label] = []
            subshards[label].append(node) 

    # Compute centroid for each subshard
    result = {}
    for label, nodes in subshards.items():
        features = np.array([
            [node.cpu_rating, node.reputation_score, node.ram_usage] for node in nodes
        ])
        centroid_vector = features.mean(axis=0)
        result[label] = {"nodes": nodes, "centroid": centroid_vector}

    print(f"Total Shards Formed: {len(result)}")
    print(f"Outliers Detected: {len(outliers)}")

    return result, outliers

def reassign_outliers(outliers, subshards, max_distance=10):
    for node in outliers:
        node_features = np.array([node.cpu_rating, node.reputation_score, node.ram_usage])
        best_shard = None
        min_distance = float('inf')

        for label, shard_info in subshards.items():
            centroid = shard_info["centroid"]
            distance = np.linalg.norm(node_features - centroid)
            if distance < min_distance:
                min_distance = distance
                best_shard = label

        if best_shard is not None and min_distance < max_distance:
            subshards[best_shard]["nodes"].append(node)
            print(f"Reassigned node {node.node_id} to cluster {best_shard} (distance: {min_distance:.2f})")
        else:
            print(f"Node {node.node_id} remains an outlier (distance: {min_distance:.2f})")

    return subshards





if __name__ == '__main__':

    # Create random dummy nodes
    nodes = [
        DummyNode(node_id=i, 
                cpu_rating=random.uniform(1.0, 5.0), 
                reputation_score=random.uniform(0.5, 1.0),
                ram_usage=random.uniform(100, 400))
        for i in range(20)
    ]

    print(nodes)
    network = DummyNetwork(nodes)

    # Run DBSCAN with an initial eps value
    subshards, outliers = compute_subshards_dbscan(network)

    reassign_outliers(outliers, subshards)

    

'''
    # Print results
    for shard_id, shard_info in subshards.items():
        print(f"Shard {shard_id}: Centroid -> {shard_info['centroid']}")
        print(f"Shard {shard_id}: Nodes -> {[node.node_id for node in shard_info['nodes']]}")
        print("=" * 50)

    print(f"Outliers: {[node.node_id for node in outliers]}")

    for node in outliers:
        print(node)


        num_simulations = 1000
        outlier_counts = []

        for _ in range(num_simulations):
            # Create random dummy nodes
            nodes = [
                DummyNode(node_id=i, 
                        cpu_rating=random.uniform(1.0, 5.0), 
                        reputation_score=random.uniform(0.5, 1.0),
                        ram_usage=random.uniform(100, 400))
                for i in range(20)
            ]

            network = DummyNetwork(nodes)

            # Run DBSCAN with an initial eps value
            subshards, outliers = compute_subshards_dbscan(network)

            # Store the number of outliers
            outlier_counts.append(len(outliers))

            

        # Compute and print average number of outliers
        avg_outliers = np.mean(outlier_counts)
        print(f"Average Number of Outliers over {num_simulations} runs: {avg_outliers:.2f}")
'''


'''
since specific clusters don't have the minimal requirement of nodes, we should group them with the cluster that is most similar to its own.
also, outliers, what should we do about them.
'''

