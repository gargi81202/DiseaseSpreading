import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import random

def waxman_edge_probability(d, L, alpha, beta):
    return alpha * np.exp(-d / (beta * L))

file_path = 'uscities.xlsx'
df = pd.read_excel(file_path)

ny_df = df[df['state_id'] == 'TX']
ny_df_sorted = ny_df.sort_values(by='population', ascending=False)

latitudes = ny_df_sorted['lat']
longitudes = ny_df_sorted['lng']
population = ny_df_sorted['population']
density = ny_df_sorted['density']

print("Total population: ", sum(population))

plt.figure(figsize=(10, 6))

plt.plot(df.index, df['population'], marker='o', linestyle='-', color='b')

# Adding labels and title
plt.xlabel('Index')
plt.ylabel('Value of population')
plt.title('Plot of Index vs. Value of population')

# Display the plot
plt.grid(True)
plt.show()

min_lat, max_lat = min(latitudes), max(latitudes)
min_lon, max_lon = min(longitudes), max(longitudes)

M = max_lon - min_lon
height = max_lat - min_lat
new_length = 1  # Fixed length
new_breadth = 2 * height / (M / 0.5) 
print(new_breadth, new_length)

# Scale the longitudes and latitudes
scaled_longitudes = 0.5*(longitudes - min_lon) / M
scaled_latitudes = (latitudes - min_lat) / height * (new_breadth / 2)
scaled_longitudes = scaled_longitudes + new_length / 4
scaled_latitudes = scaled_latitudes + new_breadth / 4

plt.figure(figsize=(10, 6))
plt.scatter(scaled_longitudes, scaled_latitudes, marker='o', color='blue')
plt.xlim(0, new_length)
plt.ylim(0, new_breadth)

plt.xlabel('Normalized Longitude')
plt.ylabel('Normalized Latitude')
plt.title('Mapping of New York Cities within a Rescaled Box')
plt.grid()

plt.show()

scale = input(f"divide the population {sum(population)} by? ")

sampling_population = (population / int(scale)).astype(int)

std_dev_scaling_factor = input("std_deviation scaling factor (in the formula np.sqrt(population / (density * np.pi)) / (3*M * factor))? ")
std_deviation = np.sqrt(population / (density * np.pi)) / (3*M * float(std_dev_scaling_factor)) 

all_sampled_points = []
for i in range(len(sampling_population)):
    sampled_latitudes = np.random.normal(loc=latitudes.iloc[i], scale=std_deviation.iloc[i], size=sampling_population.iloc[i])
    sampled_longitudes = np.random.normal(loc=longitudes.iloc[i], scale=std_deviation.iloc[i], size=sampling_population.iloc[i])

    scaled_sampled_longitudes = 0.5*(sampled_longitudes - min_lon) / M
    scaled_sampled_latitudes = (sampled_latitudes - min_lat) / height * (new_breadth / 2)
    scaled_sampled_longitudes = scaled_sampled_longitudes + new_length / 4
    scaled_sampled_latitudes = scaled_sampled_latitudes + new_breadth / 4

    clipped_sampled_longitudes = np.clip(scaled_sampled_longitudes, 0, new_length)
    clipped_sampled_latitudes = np.clip(scaled_sampled_latitudes, 0, new_breadth)

    for lat, lon in zip(clipped_sampled_latitudes, clipped_sampled_longitudes):
        all_sampled_points.append((lat, lon))

all_sampled_points = np.array(all_sampled_points)

plt.figure(figsize=(10, 6))

# Plot the centers (original longitudes and latitudes)
plt.scatter(scaled_longitudes, scaled_latitudes, marker='o', color='red', label='Centers', s=10)

# Plot the sampled points
plt.scatter(all_sampled_points[:, 1], all_sampled_points[:, 0], marker='x', color='blue', label='Sampled Points', s=10)

plt.xlim(0, new_length)
plt.ylim(0, new_breadth)

plt.xlabel('Normalized Longitude')
plt.ylabel('Normalized Latitude')
plt.title('Sampled Points and Centers')

# Adding legend
plt.legend()

# Display the plot
plt.grid()
plt.show()


alpha = input("alpha (eg: 0.1) = ")
beta = input("beta (eg: 0.9) = ")
infected_ratio = input("infected_ratio (eg: 0.1) = ")
num_instances = input("num_instances (eg: 50) = ")

G = nx.Graph()
num_nodes = len(all_sampled_points)
for i in range(num_nodes):
    G.add_node(i)

L = np.max([np.linalg.norm(all_sampled_points[i] - all_sampled_points[j]) for i in range(num_nodes) for j in range(i)])

for i in range(num_nodes):
    for j in range(i + 1, num_nodes):
        d = np.linalg.norm(all_sampled_points[i] - all_sampled_points[j])
        prob = waxman_edge_probability(d, L, float(alpha), float(beta))
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

infected_nodes = random.sample(list(directed_G.nodes()), max(1, int(float(infected_ratio) * num_nodes)))
filename = input("filename (eg: LT_TX_example.txt) = ")
with open(filename, "w") as file:
    for node in infected_nodes:
        file.write(f"INFECTED_NODE {node}\n")
    
    for n in G.nodes():
        file.write(f"NODE {n}\n")
    for (u, v) in directed_G.edges():
        if (u, v) in weights:
            file.write(f"EDGE {u} {v} {weights[(u, v)]:.5f}\n")
    file.write(f"NUM_INSTANCES {num_instances}\nNUM_VACCINES {int(num_nodes*float(infected_ratio))}\n")

print(f"output in {filename}")
