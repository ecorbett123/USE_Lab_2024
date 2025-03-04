import overpy
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def get_average_flow_by_osmid(osm_id, osm_id_map):
    return 5


osm_to_edge_and_weight = {}
# read in csv file
df = pd.read_csv('/data/Strava/columbia_streets_2023-07-01-2023-07-14_ride.csv')

for _, row in df.iterrows():
    if row['osm_reference_id'] in osm_to_edge_and_weight:
        if (row['edge_uid'], row['ride_count']) not in osm_to_edge_and_weight[row['osm_reference_id']]:
            osm_to_edge_and_weight[row['osm_reference_id']].append((row['edge_uid'], row['ride_count']))
    else:
        osm_to_edge_and_weight[row['osm_reference_id']] = [(row['edge_uid'], row['ride_count'])]

# get osm ids as comma separated list
osm_ids = ','.join(str(s) for s in osm_to_edge_and_weight.keys())

api = overpy.Overpass()
result = api.query(
    """[out:json];way(id:""" + osm_ids + """);out geom;""")

bike_network = nx.Graph()
for way in result.ways:
    way_str = way.__str__()
    nodes = way_str[way_str.index('[')+1:way_str.index(']')]
    nodes = nodes.split(",")
    nodes = [x.strip() for x in nodes]
    # get average bike weight for the osm id in question (revisit this function later)
    weight = get_average_flow_by_osmid(way.id, osm_to_edge_and_weight)

    for i in range(len(nodes)-1):
        bike_network.add_edge(nodes[i], nodes[i+1], flow=weight)

print(nx.number_connected_components(bike_network))