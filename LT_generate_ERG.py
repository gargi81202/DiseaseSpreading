import networkx as nx
import random
import subprocess
import os
import pickle

def generate_erdos_renyi_graph(num_nodes, prob, infected_ratio):
    G = nx.erdos_renyi_graph(num_nodes, prob, directed=True)

    weights = {}
    for node in G.nodes():
        incoming_edges = list(G.in_edges(node))
        if incoming_edges:
            raw_weights = [random.random() for _ in incoming_edges]
            total_raw_weight = sum(raw_weights)*1.1
            
            normalized_weights = [w / total_raw_weight for w in raw_weights]
            
            for edge, weight in zip(incoming_edges, normalized_weights):
                weights[edge] = weight

    infected_nodes = random.sample(list(G.nodes()), max(1, int(infected_ratio * num_nodes)))
    
    ni = input("num instances (eg 50) = ")
    vr = input("vaccine ratio (eg 0.1) = ")
    output_filename = "LT_ERG_" + str(num_nodes) + "_" + str(int(num_nodes*float(vr))) + "_" + str(ni) + ".txt"
    with open(output_filename, "w") as file:
        for node in infected_nodes:
            file.write(f"INFECTED_NODE {node}\n")
        
        for n in G.nodes():
            file.write(f"NODE {n}\n")
        for (u, v) in G.edges():
            if (u, v) in weights:
                file.write(f"EDGE {u} {v} {weights[(u, v)]:.5f}\n")
        file.write(f"NUM_INSTANCES {ni}\nNUM_VACCINES {(int(num_nodes*float(vr)))}\n")

    # with open('ERG_graph.pkl', 'wb') as pickle_file:
    #     pickle.dump((G, weights, infected_nodes), pickle_file)
    
    return G, weights, infected_nodes

def make_dotfile(G, weights, infected_nodes, filename):
    output = 'digraph G {\n'
    output += 'rankdir=LR;\nsize="8,5";\nratio="compress";\n'
    
    for node in G.nodes():
        if node in infected_nodes:
            output += f'{node} [label="{node}", style=filled, fillcolor=lightcoral];\n'
        else:
            output += f'{node} [label="{node}"];\n'
    
    for (u, v) in G.edges():
        if (u, v) in weights:
            output += f'{u} -> {v} [label="{weights[(u, v)]:.2f}"];\n'
    
    output += '}'
    
    dot_filename = f"{filename}.dot"
    with open(dot_filename, 'w') as dot_file:
        dot_file.write(output)

    subprocess.run(['dot', '-Tpdf', '-O', dot_filename])
    
    os.remove(dot_filename)

if __name__ == "__main__":
    nn = input("num nodes = ")
    ir = input("infected ratio (eg 0.1) = ")
    G, weights, infected_nodes = generate_erdos_renyi_graph(num_nodes=int(nn), prob=0.3, infected_ratio=float(ir))
    
    # make_dotfile(G, weights, infected_nodes, "LT_erdos_renyi_graph")
