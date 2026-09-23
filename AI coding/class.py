import numpy as np
import csv
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm

cities = pd.read_csv("/Users/Laura/Desktop/cities.csv")
connections = pd.read_csv("/Users/Laura/Desktop/connections.csv")

#plot it as nodes
# Create the graph
graph = nx.Graph()

# Add cities as nodes
for city in cities.to_dict("records"):
    graph.add_node(
        city["city_id"],
        name=city["city"],
        role=city["role"],
        position=(float(city["longitude"]), float(city["latitude"]))
    )

# Add connections as edges
for connection in connections.to_dict("records"):
    graph.add_edge(
        connection["city_from"],
        connection["city_to"],
        distance=float(connection["distance_km"])
    )

positions = nx.get_node_attributes(graph, "position")

colors = {
    "start": "green",
    "goal": "red",
    "node": "skyblue",
}

node_colors = [
    colors[graph.nodes[node]["role"]]
    for node in graph.nodes
]

plt.figure(figsize=(12, 9))

nx.draw_networkx_edges(
    graph,
    positions,
    edge_color="gray",
    alpha=0.6
)

nx.draw_networkx_nodes(
    graph,
    positions,
    node_color=node_colors,
    node_size=500,
    edgecolors="black"
)

labels = {
    node: graph.nodes[node]["name"]
    for node in graph.nodes
}

nx.draw_networkx_labels(
    graph,
    positions,
    labels=labels,
    font_size=8
)

plt.title("City Connections")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.grid(True, alpha=0.3)
plt.axis("equal")
plt.show()