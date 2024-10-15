import os
import time
import pickle
import json
import gurobipy as gp
import logging

graph_filename = input("graph filename: ")
json_filename = input("json filename: ")

# Set up logging to write both to a file and to the console
logging.basicConfig(level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, etc.)
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(graph_filename + ".inexact_2nd_rounding.log"),  # Write logs to a file
                        logging.StreamHandler()  # Print logs to the console
                    ])

def load_graph_topologies(filename):
    with open(filename, 'rb') as f:  # Open in binary mode
        topologies = pickle.load(f)  # Use pickle to load the data

    # Convert edges to a more usable format for your Gurobi model
    processed_topologies = []
    for topology in topologies:
        graph = {}
        for edge in topology['edges']:
            start_node = int(edge[0])  # Convert to integer for consistency
            end_node = int(edge[1])  # Convert to integer for consistency
            if start_node not in graph:
                graph[start_node] = []
            graph[start_node].append(end_node)
        processed_topologies.append((graph, topology['infected_nodes']))

    return processed_topologies

def read_graph_from_file(filename):
    data = {"graph": {}, "infected": [], "nodes": []}
    nodes_set = set()
    with open(filename, 'r') as f:
        line = f.readline()
        while line:
            if "INFECTED_NODE" in line:
                infected = line.split(" ")[1]
                data["infected"].append(int(infected))
            elif "NODE" in line:
                nodes_set.add(int(line.split(" ")[1].rstrip()))
            elif "EDGE" in line:
                edge = line.split(" ")[1:]
                node_st = int(edge[0])
                node_end = int(edge[1])
                nodes_set.add(node_st)
                nodes_set.add(node_end)
                prob = float(edge[2])
                if prob == 0.0:
                    line = f.readline()
                    continue
                if node_st not in data["graph"]:
                    data["graph"][node_st] = {}
                data["graph"][node_st][node_end] = prob
            line = f.readline()
    data["nodes"] = list(nodes_set)
    return data

def get_infected(topology, infected, vaccinated):
    visited = set(vaccinated)
    _infected = infected.copy()
    count = 0
    for _i in infected:
        visited.add(_i)
        count += 1
    continued = 0
    while len(_infected) > 0:
        _index = _infected.pop(0)
        if _index not in topology:
            continued += 1
            continue
        for neighbor in topology[_index]:
            if neighbor not in visited:
                visited.add(neighbor)
                _infected.append(neighbor)
                count += 1
    return count

def disease_solve_iterator(graph_topologies, no_topologies, nodes, infected, budget, exact=False):
    logging.info(f"Topologies: {no_topologies}")
    logging.info(f"Nodes: {len(nodes)}")
    logging.info(f"Vaccines: {budget}")
    logging.info(f"Infected: {len(infected)}")
    logging.info(f"Exact: {exact}")

    # Create a new model
    model = gp.Model()

    # Create continuous variables for LP relaxation
    node_vars = model.addVars([(i, j) for i in range(no_topologies) for j in nodes], 
                              lb=0.0, ub=1.0, vtype=gp.GRB.CONTINUOUS, name="node")

    vaccinated_vars = model.addVars(nodes, lb=0.0, ub=1.0, vtype=gp.GRB.CONTINUOUS, name="vaccinated")

    # Set the objective function (minimize total infected nodes)
    model.setObjective(sum(node_vars[(i, node)] for i in range(no_topologies) for node in nodes), 
                       gp.GRB.MINIMIZE)

    # Budget constraint: Total vaccinated nodes must equal budget
    model.addConstr(sum(vaccinated_vars[i] for i in nodes) == budget)

    # Ensure initially infected nodes remain infected
    for inf_node in infected:
        model.addConstr(vaccinated_vars[inf_node] == 0)
        for i in range(no_topologies):
            model.addConstr(node_vars[(i, inf_node)] == 1)

    # Add constraints for propagation through neighbors
    for index, (graph, _) in enumerate(graph_topologies):
        for node, neighbors in graph.items():
            for neighbor in neighbors:
                model.addConstr(node_vars[(index, neighbor)] >= 
                                node_vars[(index, node)] - vaccinated_vars[neighbor])

    # Optimize the relaxed LP model
    model.optimize()

    vaccines_given = 0
    vaccinated_set = set()  # Track nodes already vaccinated

    # Iterate until we meet the budget
    while vaccines_given < budget:
        maxV = -1
        maxVnode = None

        # Find the node with the highest vaccination score
        for node in nodes:
            if node not in vaccinated_set and vaccinated_vars[node].X > maxV:
                maxVnode = node
                maxV = vaccinated_vars[node].X

        # Round the selected node's vaccination to 1
        print(f"Vaccine given to node {maxVnode} with score {maxV}")
        model.addConstr(vaccinated_vars[maxVnode] == 1)
        vaccinated_set.add(maxVnode)

        # Re-optimize after updating the model with the new constraint
        model.optimize()
        vaccines_given += 1

    # Log results
    logging.info(f"Optimal objective value: {model.objVal}")
    logging.info(f"Average infected nodes after vaccination: {model.objVal / no_topologies}")

    result = {"score": model.objVal, "solution": vaccinated_set}
    return result





def save_json_to_pickle(json_filename, pkl_filename):
    # Load from JSON
    with open(json_filename, 'r') as f:
        data = json.load(f)

    # Save to pickle
    with open(pkl_filename, 'wb') as f:
        pickle.dump(data, f)

if __name__ == "__main__":
    filename = "graph_topologies.pkl"
    save_json_to_pickle(json_filename, filename)
    topologies = load_graph_topologies(filename)

    graph_data = read_graph_from_file(graph_filename)  # Reload graph details
    infected_nodes = graph_data["infected"]
    nodes = graph_data["nodes"]
    budget = int(len(nodes) * float(input("vaccination ratio: ")))
    exact = False

    start_time = time.time()
    disease_solve_iterator(topologies, len(topologies), nodes, infected_nodes, budget, exact)
    end_time = time.time()

    logging.info(f"Elapsed time: {end_time - start_time} seconds")
