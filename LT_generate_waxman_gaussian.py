import numpy as np 
import networkx as nx
import random
import matplotlib.pyplot as plt
import pickle

def generate_gaussian_points(num_nodes, num_centers, box_size=(1, 1)):
    centers = np.random.uniform(0, box_size[0], (num_centers, 2))
    
    max_sigma = min(box_size) / 10
    sigmas = np.random.uniform(0.05 * max_sigma, max_sigma, num_centers)
    
    sigma_sum = sum(sigmas)
    points = []

    for i in range(num_centers):
        num_points = int(num_nodes * sigmas[i] / sigma_sum)
        sampled_points = np.random.normal(loc=centers[i], scale=sigmas[i], size=(num_points, 2))
        
        sampled_points = np.clip(sampled_points, [0, 0], box_size)
        points.extend(sampled_points)

    while len(points) < num_nodes:
        points.append(np.random.uniform(0, box_size[0], 2))
    
    return np.array(points), centers, sigmas


def waxman_edge_probability(d, L, alpha, beta):
    return alpha * np.exp(-d / (beta * L))

def generate_waxman_graph_gaussian(num_nodes, num_centers, alpha, beta, infected_ratio):
    points, centers, _ = generate_gaussian_points(num_nodes, num_centers)
    
    G = nx.Graph()
    for i in range(num_nodes):
        G.add_node(i)

    L = np.max([np.linalg.norm(points[i] - points[j]) for i in range(num_nodes) for j in range(i)])

    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            d = np.linalg.norm(points[i] - points[j])
            prob = waxman_edge_probability(d, L, alpha, beta)
            if random.random() < prob:
                G.add_edge(i, j)

    directed_G = nx.DiGraph()
    directed_G.add_nodes_from(G.nodes())
    for u, v in G.edges():
        directed_G.add_edge(u, v)
        directed_G.add_edge(v, u)

    weights = {}
    for node in directed_G.nodes():
        incoming_edges = list(directed_G.in_edges(node))
        if incoming_edges:
            raw_weights = [random.random() for _ in incoming_edges]
            total_raw_weight = sum(raw_weights) * 1.1
            
            normalized_weights = [w / total_raw_weight for w in raw_weights]
            for edge, weight in zip(incoming_edges, normalized_weights):
                weights[edge] = weight

    infected_nodes = random.sample(list(directed_G.nodes()), max(1, int(infected_ratio * num_nodes)))
    
    ni = input("num instances (eg 50) = ")
    vr = input("vaccine ratio (eg 0.1) = ")

    output_filename = "LT_waxman_gaussian_" + str(num_nodes) + "_" + str(int(num_nodes*float(vr))) + "_" + str(ni) + ".txt"

    with open(output_filename, "w") as file:
        for node in infected_nodes:
            file.write(f"INFECTED_NODE {node}\n")
        
        for n in G.nodes():
            file.write(f"NODE {n}\n")
        for (u, v) in directed_G.edges():
            if (u, v) in weights:
                file.write(f"EDGE {u} {v} {weights[(u, v)]:.5f}\n")
        file.write(f"NUM_INSTANCES {ni}\nNUM_VACCINES {(int(num_nodes*float(vr)))}\n")
    
    # with open('waxman_gaussian_graph.pkl', 'wb') as pickle_file:
    #     pickle.dump((directed_G, weights, infected_nodes), pickle_file)
    print("output in", output_filename)
    return directed_G, weights, infected_nodes, points, centers


def plot_waxman_graph(G, pos, centers, infected_nodes, weights):
    plt.figure(figsize=(8, 8))

    node_colors = ['lightcoral' if node in infected_nodes else 'skyblue' for node in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=5, alpha=0.8)

    # nx.draw_networkx_edges(G, pos, edgelist=G.edges(), arrowstyle='->', arrowsize=1)

    center_colors = ['green' for _ in centers]
    plt.scatter(centers[:, 0], centers[:, 1], color=center_colors, s=10)

    plt.title("Waxman Graph with Gaussian Distributed Points")
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    a = input("alpha (eg: 0.1) = ")
    b = input("beta (eg: 0.9) = ")
    nc = input("num_centers = ")
    nn = input("num nodes = ")
    ir = input("infected ratio (eg 0.1) = ")
    G, weights, infected_nodes, points, centers = generate_waxman_graph_gaussian(
        num_nodes=int(nn), 
        num_centers=int(nc),
        alpha=float(a), 
        beta=float(b), 
        infected_ratio=float(ir)
    )

    plot_waxman_graph(G, {i: points[i] for i in G.nodes()}, centers, infected_nodes, weights)
