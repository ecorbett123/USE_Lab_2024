import networkx as nx
import fiona
import pandas as pd

# This file creates shapefiles for the 10 locations with highest degree and highest throughput from the mobility data

def high_degree_nodes(graph):
    degree_list = sorted(graph.degree, key=lambda x: x[1], reverse=True)
    degree_list = degree_list[0:10]
    final_list = [x[0] for x in degree_list]
    return final_list


def high_throughput_nodes(graph):
    traffic_node = {}
    for pred in graph.pred:
        for vals in graph.pred[pred]:
            total = 0
            if pred in traffic_node:
                total = traffic_node[pred]
            traffic_node[pred] = total + float(graph.pred[pred][vals]['weight'])

    high_traffic = sorted(traffic_node, key=lambda x: traffic_node[x], reverse=True)
    high_traffic = high_traffic[0:10]
    for node in high_traffic:
        print(traffic_node[node])
    return high_traffic

if __name__ == "__main__":
    # read in graph
    mobility_graph = nx.DiGraph()  # directed graph, origin -> destination
    f = open('../data/ny_state_inside_weekly_flows_ct2ct_2020_03_02.csv') # change this path to be your own local file of mobility data, see README for how to download

    f.readline()  # skip header
    lines = 0
    file_lines = f.readlines()
    tuples = []
    maxFlow = 0
    for line in file_lines:
        line = line.strip()
        nodes = line.split(",")
        mobility_graph.add_edge(str(nodes[0]), str(nodes[1]), weight=nodes[8])
        tuples.append((str(nodes[0]), str(nodes[1]), nodes[8]))

    high_degree = high_degree_nodes(mobility_graph)
    high_throughput = high_throughput_nodes(mobility_graph)

    # write these to shape file to see where they are
    # define schema
    schema = {
        'geometry': 'Point',
        'properties': [('Name', 'str')]
    }

    pointDf = pd.read_csv('../data/ny_state_inside_weekly_flows_ct2ct_2020_03_02.csv')
    # open a fiona object
    pointShp = fiona.open('../shape_files/nyc_high_degree.shp', mode='w', driver='ESRI Shapefile',
                          schema=schema, crs="EPSG:4326")
    # open a fiona object
    pointThr = fiona.open('../shape_files/nyc_high_throughput.shp', mode='w', driver='ESRI Shapefile',
                          schema=schema, crs="EPSG:4326")
    # iterate over each row in the dataframe and save record
    for index, row in pointDf.iterrows():
        if str(row.geoid_d) in high_degree:
            rowDict = {
                'geometry': {'type': 'Point',
                             'coordinates': (row.lng_d, row.lat_d)},
                'properties': {'Name': row.geoid_d},
            }
            pointShp.write(rowDict)

        if str(row.geoid_d) in high_throughput:
            rowDict = {
                'geometry': {'type': 'Point',
                             'coordinates': (row.lng_d, row.lat_d)},
                'properties': {'Name': row.geoid_d},
            }
            pointThr.write(rowDict)
    # close fiona object
    pointShp.close()
    pointThr.close()
