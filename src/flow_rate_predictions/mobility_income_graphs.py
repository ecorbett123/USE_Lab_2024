import matplotlib.pyplot as plt
import networkx as nx
from netgraph import Graph

# This file creates a graph showing mobility according to income. It clusters by income and sees how those of similar income levels travel amongst other income levels.

if __name__ == "__main__":
    # read in graph
    mobility_graph = nx.DiGraph()  # directed graph, origin -> destination
    f = open('../data/ny_state_inside_weekly_flows_ct2ct_2020_03_02.csv')
    income_file = open('../data/MedianIncome_2020_nyc.csv')
    #S1903_C03_001E

    node_to_community = {}
    # get mapping of census tract to income data
    income_file.readline()
    income_file.readline()
    income_lines = income_file.readlines()

    for line in income_lines:
        line = line.strip()
        cols = line.split(",")
        geo_id = cols[0].strip("\"")
        geo_id = geo_id[9:]
        income = cols[182].strip("\"")
        if income.isnumeric():
            income = int(income)
        else:
            income = -1

        # create categorical variable for income level
        rank = 5
        if income == -1:
            rank = 0
        elif income < 43000:
            rank = 1
        elif income < 68300:
            rank = 2
        elif income < 97300:
            rank = 3
        elif income < 144000:
            rank = 4

        node_to_community[geo_id] = rank

    community_to_color = { 0: 'tab:grey', 1: 'tab:blue', 2: 'tab:orange', 3: 'tab:green', 4: 'tab:red', 5: 'tab:purple'}
    node_color = {node: community_to_color[community_id] for node, community_id in node_to_community.items()}
    f.readline()  # skip header
    lines = 0
    file_lines = f.readlines()
    tuples = []
    maxFlow = 0
    for line in file_lines:
        line = line.strip()
        nodes = line.split(",")
        # if in nyc census tract file
        if str(nodes[0]) in node_to_community and str(nodes[1]) in node_to_community:
            mobility_graph.add_edge(str(nodes[0]), str(nodes[1]), weight=nodes[8])
            tuples.append((str(nodes[0]), str(nodes[1]), nodes[8]))
            if float(nodes[8]) > maxFlow:
                maxFlow = float(nodes[8])

    Graph(mobility_graph, edge_layout='bundled', edge_layout_kwargs=dict(k=2000))
    plt.show()

    fig, ax = plt.subplots()
    Graph(mobility_graph,
          node_color=node_color,  # indicates the community each belongs to
          node_size=1.0,
          node_edge_width=0,  # no black border around nodes
          edge_width=0.2,  # use thin edges, as they carry no information in this visualisation
          edge_alpha=0.6,  # low edge alpha values accentuates bundles as they appear darker than single edges
          node_layout='community', node_layout_kwargs=dict(node_to_community=node_to_community),
          #edge_layout='bundled',
          ax=ax,
          )

    edge_width = {(u, v) : float(w)/(29276/2) for (u, v, w) in tuples}
    Graph(tuples,
          edge_width=edge_width,
          arrows=True,
          node_edge_width=0,
          node_layout='community',
          node_layout_kwargs=dict(node_to_community=node_to_community),
          node_color=node_color,
          node_size=1.0,)
    plt.show()
