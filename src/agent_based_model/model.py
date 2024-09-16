import mesa
import os
import pandas as pd
from agents import BikerAgent, RoadAgent
import mesa_geo as mg
from shapely.geometry import Point
import matplotlib.cm as cm
from matplotlib.colors import Normalize
from scheduler import CustomScheduler
from datetime import datetime
import osmnx as ox
import json
import sys

class BikerModel(mesa.Model):
    """Model containing biker agents that move throughout NYC accumulating heat indices"""

    def __init__(self, dir_name, G):
        super().__init__()
        self.num_agents = 0
        self.schedule = CustomScheduler(self)
        self.space = mg.GeoSpace(warn_crs_conversion=True, crs="epsg:4326")
        self.steps = 0
        self.counts = None
        self.G = G
        self.road_map = {}
        self.isFinished = False
        self.running = True

        # set up Road segment agents
        road_creator = mg.AgentCreator(RoadAgent,
                                       model=self,
                                       crs=self.space.crs,
                                       agent_kwargs={"heat_contribution": None,
                                                     "edge_id": None}
                                       )
        # add each edge in the osm network graph to the model
        for edge in G.edges:
            edge_data = self.G.edges[edge]
            if 'geometry' in edge_data:
                road = road_creator.create_agent(edge_data['geometry'], self.num_agents)
                # t2 is heat index measure - see write_data_from_wrf_to_csv.py and create_osm_heat_bike_graph.py
                t2 = float(self.G.nodes[edge[0]]['t2'])

                # get travel time for that edge
                if 'travel_time' in edge_data and edge_data['travel_time'] and edge_data['travel_time'] > 0:
                    time = edge_data['travel_time']
                else:
                    max_speed = 15  # average cyclist speed is about 10mph, e-bike about 20
                    if 'speed_kph' in edge_data and edge_data['speed_kph'] and edge_data['speed_kph'] > 0:
                        max_speed = edge_data['speed_kph'] / 3.6 # convert kph to meters ph
                    length = edge_data['length']  # returns length in meters
                    time = length / max_speed # meters / meters ph

                # heat contribution of segment is time travelled times t2 heat index
                road.heat_contribution = time * t2
                road.edge_id = edge
                road.start_node = edge[0]
                road.end_node = edge[1]
                road.osmid = edge_data['osmid']

                self.num_agents += 1
                self.space.add_agents(road)
                self.schedule.add(road)

        # set up biker agents
        ac_population = mg.AgentCreator(BikerAgent,
                                        model=self,
                                        crs=self.space.crs,
                                        agent_kwargs={"origin": None,
                                                      "destination": None,
                                                      "route": None,
                                                      "G": G,
                                                      "trip_count": None}
                                        )

        bikers = pd.read_csv("/Users/emmacorbett/PycharmProjects/USE_Lab/src/agent_based_model/top_journey_counts.csv")
        for _, row in bikers.iterrows():
            if 'shortest_path' in row and row['shortest_path'] and not isinstance(row['shortest_path'], float):
                orig = row['origin_osm_node']
                route = row['shortest_path'].strip('][').split(', ')
                route = [int(x) for x in route]

                # drop journeys that start and end at same location, since we cannot assume their path
                if len(route) > 1:
                    x, y = self.G.nodes[orig]['x'], self.G.nodes[orig]['y']

                    a = ac_population.create_agent(Point(x, y), self.num_agents)
                    a.route = route
                    a.trip_count = row['trip_count']
                    self.num_agents += 1
                    self.space.add_agents(a)
                    self.schedule.add(a)

        self.assign_colors()


    def assign_colors(self):
        biker_values = []
        road_values = []
        max_bike_val = 0
        max_road_val = 0
        max_bike = None
        max_road = None
        # cap the hottest heat measurement
        top = (10000.0 * (self.steps + 1))
        for agent in self.schedule.agents:
            if agent.heat_accumulation != 0:
                if isinstance(agent, BikerAgent):
                    if agent.heat_accumulation > top:
                        biker_values.append(top)
                    else:
                        biker_values.append(agent.heat_accumulation)
                    if agent.heat_accumulation > max_bike_val:
                        max_bike = agent
                        max_bike_val = agent.heat_accumulation
                elif isinstance(agent, RoadAgent):
                    if agent.heat_accumulation > top:
                        road_values.append(top)
                    else:
                        road_values.append(agent.heat_contribution)
                    if agent.heat_accumulation > max_road_val:
                        max_road = agent
                        max_road_val = agent.heat_accumulation
        #attribute_values = [agent.heat_accumulation for agent in self.schedule.agents if isinstance(agent, BikerAgent) and agent.heat_accumulation != 0]

        if len(road_values) < 1:
            road_values.append(0)
        if len(biker_values) < 1:
            biker_values.append(0)
        road_values.sort(reverse=True)
        norm_bike = Normalize(vmin=min(biker_values), vmax=max(biker_values))
        norm_road = Normalize(vmin=min(road_values), vmax=max(road_values))
        cmap_bike = cm.get_cmap('Reds')
        cmap_road = cm.get_cmap('Blues')

        for agent in self.schedule.agents:
            if isinstance(agent, BikerAgent):
                if agent.heat_accumulation > top:
                    agent.color = cmap_bike(norm_bike(top))
                else:
                    agent.color = cmap_bike(norm_bike(agent.heat_accumulation))
            elif isinstance(agent, RoadAgent):
                if agent.heat_accumulation > top:
                    agent.color = cmap_road(norm_road(top))
                else:
                    agent.color = cmap_road(norm_road(agent.heat_accumulation))
                    # if want full heat contribution of roads, can do below line
                    # agent.color = cmap_road(norm_road(agent.heat_contribution))
        if max_bike and max_road:
            print("Geometry: " + str(max_bike.geometry) + " heat: " + str(max_bike.heat_accumulation))
            print("Geometry: " + str(max_road.geometry) + " heat: " + str(max_road.heat_accumulation))


    def step(self):
        """Advance the model by one step."""
        self.steps += 1
        self.schedule.step()

        if not self.isFinished:
            self.isFinished = True
            # set heat contribution of road segments after bikers have moved
            for agent in self.schedule.agents:
                if isinstance(agent, RoadAgent):
                    if str(agent.osmid) in self.road_map:
                        agent.heat_accumulation += (self.road_map[str(agent.osmid)] * agent.heat_contribution)
                else:
                    if agent.route and len(agent.route) > agent.cur_time_step:
                        self.isFinished = False
                        break
        self.assign_colors()
        self.road_map = {}

        # all paths have been run, find the hottest road segments and higlight them, the hottest normalized paths
        if self.isFinished:
            # 20 hottest road segements
            final_roads = []
            final_bikers = []
            for agent in self.schedule.agents:
                if isinstance(agent, RoadAgent):
                    final_roads.append(agent)
                else:
                    final_bikers.append(agent)
            sorted_roads = sorted(final_roads, key = lambda x: x.heat_accumulation, reverse=True)
            sorted_roads = sorted_roads[0:20]
            sorted_roads = [self.convertTuple(x.edge_id, x.heat_accumulation) for x in sorted_roads]

            #self.highlight_max_segments(sorted_roads)
            with open('max_road_segments.txt', 'w+') as f:
                data_to_write = '\n'.join(sorted_roads)

                # Write the data to the file
                f.write(data_to_write)

            sorted_bikers = sorted(final_bikers, key = lambda x: x.heat_accumulation, reverse=True)
            sorted_bikers = sorted_bikers[0:20]
            sorted_bikers = [self.convertTuple(x.route, x.heat_accumulation) for x in sorted_bikers]
            with open('max_biker_route.txt', 'w+') as file:
                data_to_write = '\n'.join(sorted_bikers)

                # Write the data to the file
                file.write(data_to_write)

            sys.exit()
            # self.highlight_max_segments(sorted_bikers[0].route)

            # hottest route

        # max_agent = []
        # for agent in self.schedule.agents:
        #     if isinstance(agent, RoadAgent):
        #         max_agent.append(agent)
        #         if len(max_agent) == 20:
        #             break
        # self.highlight_max_segments(max_agent)

        # TODO: set condition to stop running once all paths have been run

    def convertTuple(self, tup, heat):
        # initialize an empty string
        strg = ''
        for item in tup:
            strg = strg + str(item) + ','
        strg = strg + str(heat)
        return strg

    # this fucntion colors the edges of the route with the highest heat accumulation (route will be pre saved)
    def assign_color_max_route(self, max_bike):
        for agent in self.schedule.agents:
            if isinstance(agent, BikerAgent):
                # red_val = norm_bike(agent.heat_accumulation)
                # agent.color = (red_val, 0, 0, 1)
                agent.color = (255, 255, 255, 1)
            elif isinstance(agent, RoadAgent):
                if agent.start_node in max_bike.route and agent.end_node in max_bike.route:
                    agent.color = (0.6, 0, 0, 1)
                else:
                    agent.color = (255, 255, 255, 1)

    # highlights all the edges passed in max_segments - can be used to show any set of segments; max segments is a list of edge ids
    def highlight_max_segments(self, max_segments):
        for agent in self.schedule.agents:
            if isinstance(agent, BikerAgent):
                agent.color = (255, 255, 255, 1)
            elif isinstance(agent, RoadAgent):
                if agent.edge_id in max_segments:
                    agent.color = (0.6, 0, 0, 1)
                else:
                    agent.color = (255, 255, 255, 1)
