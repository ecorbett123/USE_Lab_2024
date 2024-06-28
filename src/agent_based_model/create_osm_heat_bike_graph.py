import osmnx as ox
import numpy as np
from geopy.distance import geodesic
import networkx as nx


def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).meters


def get_closest_index(lat_array, long_array, lat, lon):
    min_distance = 10000000
    min_index = (-1, -1)
    shp = lat_array.shape
    for i in range(shp[0]):
        for j in range(shp[1]):
            cur_dist = calculate_distance(lat, lon, lat_array[i][j], long_array[i][j])
            if cur_dist < min_distance:
                min_distance = cur_dist
                min_index = (i, j)

    return min_index

# Code to generate ny_bike_graph.graphml file:
#G = ox.graph_from_place("New York City, New York, USA", network_type='bike', retain_all=True)
G = ox.load_graphml(filepath="../ny_bike_graph.graphml")

lat_array = np.loadtxt("/Users/emmacorbett/PycharmProjects/USE_Lab/data/wrf_heat_maps/lat_array.csv", delimiter=',')
long_array = np.loadtxt("/Users/emmacorbett/PycharmProjects/USE_Lab/data/wrf_heat_maps/lon_array.csv", delimiter=',')
t2_array = np.loadtxt("/Users/emmacorbett/PycharmProjects/USE_Lab/data/wrf_heat_maps/t2_array.csv", delimiter=',')

# find min distance between the points - approximately 515 meters
# distances = []
# for i in range(len(lat)):
#     for j in range(len(long)):
#         dist = calculate_distance(lat[1][2], long[1][2], lat[i][j], long[i][j],)
#         distances.append(dist)
#
# distances.sort(reverse=False)
# print(distances)
# print(distances[1])

node_to_heat_dict = {}
for node in G.nodes:
    index = get_closest_index(lat_array, long_array, G.nodes[node]['y'], G.nodes[node]['x'])
    node_to_heat_dict[node] = t2_array[index[0]][index[1]]

nx.set_node_attributes(G, node_to_heat_dict, name='t2')
ox.save_graphml(G, "ny_bike_graph_heat_included.graphml")
