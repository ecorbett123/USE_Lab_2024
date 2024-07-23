import mesa
import os
import pandas as pd
import osmnx as ox
from agents import BikerAgent, NeighbourhoodAgent, RoadAgent
import mesa_geo as mg
from shapely.geometry import Point, LineString
import matplotlib.cm as cm
from matplotlib.colors import Normalize
import random
import math

class BikerModel(mesa.Model):
    """A model with some number of agents."""

    geojson_regions = "/Users/emmacorbett/PycharmProjects/USE_Lab/data/Borough Boundaries.geojson"
    unique_id = "boro_code"

    def __init__(self, dir_name, G):
        super().__init__()
        self.num_agents = 0
        self.schedule = mesa.time.BaseScheduler(self)
        self.space = mg.GeoSpace(warn_crs_conversion=True, crs="epsg:4326")
        self.steps = 0
        self.counts = None
        self.reset_counts()
        self.G = G

        self.running = True
        # self.datacollector = mesa.DataCollector(
        #     {
        #         "cool": get_cool_count,
        #         "warm": get_warm_count,
        #         "hot": get_hot_count,
        #         "burning": get_burning_count,
        #     }
        # )

        # Set up the Neighborhood regions:
        # ac = mg.AgentCreator(NeighbourhoodAgent, model=self)
        # neighbourhood_agents = ac.from_file(
        #     self.geojson_regions, unique_id=self.unique_id
        # )
        # self.space.add_agents(neighbourhood_agents)

        # set up Road segment agents
        road_creator = mg.AgentCreator(RoadAgent,
                                       model=self,
                                       crs=self.space.crs,
                                       agent_kwargs={"heat_contribution": None,
                                                     "edge_id": None}
                                       )
        for edge in G.edges:
            edge_data = self.G.edges[edge]
            if 'geometry' in edge_data:
                road = road_creator.create_agent(edge_data['geometry'], self.num_agents)
                t2 = float(self.G.nodes[edge[0]]['t2'])
                if 'travel_time' in edge_data and edge_data['travel_time'] and edge_data['travel_time'] > 0:
                    time = edge_data['travel_time']
                else:
                    max_speed = 15  # average cyclist speed is about 10mph, e-bike about 20
                    if 'speed_kph' in edge_data and edge_data['speed_kph'] and edge_data['speed_kph'] > 0:
                        max_speed = edge_data['speed_kph'] / 3.6
                    length = edge_data['length']  # returns length in meters
                    time = length / max_speed
                road.heat_contribution = time*t2
                road.edge_id = edge
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
                                                      "G": G}
                                        )
        dirs = os.listdir(dir_name)

        for file in dirs:
            if file.endswith('.csv'):
                df = pd.read_csv(dir_name + "/" + file)
                # shortest_paths = []
                # orig_list = []
                # df_unfiltered['started_at'] = pd.to_datetime(df_unfiltered['started_at'])
                # df_unfiltered['ended_at'] = pd.to_datetime(df_unfiltered['ended_at'])
                # df = df_unfiltered[(df_unfiltered['started_at'].dt.hour >= 11) & (df_unfiltered['started_at'].dt.hour < 14) & (df_unfiltered['end_lng']) & (df_unfiltered['start_lng'])]
                for _, row in df.iterrows():
                    # code to calculate and save shortest path information on first run
                    # orig = ox.distance.nearest_nodes(G, X=row['start_lng'], Y=row['start_lat'])
                    # dest = ox.distance.nearest_nodes(G, X=row['end_lng'], Y=row['end_lat'])
                    # route = ox.shortest_path(G, orig, dest, weight="travel_time")
                    # shortest_paths.append(route)
                    # orig_list.append(orig)
                    if 'shortest_path' in row and row['shortest_path'] and not isinstance(row['shortest_path'], float):
                        orig = row['orig']
                        route = row['shortest_path'].strip('][').split(', ')
                        route = [int(x) for x in route]
                        x, y = self.G.nodes[orig]['x'], self.G.nodes[orig]['y']

                        a = ac_population.create_agent(Point(x, y), self.num_agents)
                        a.route = route
                        self.num_agents += 1
                        self.space.add_agents(a)
                        self.schedule.add(a)
                # Code to save shortest path info on first run through
                # df['orig'] = orig_list
                # df['shortest_path'] = shortest_paths
                # df.to_csv('2024_path_test_' + file)

        # for agent in neighbourhood_agents:
        #     self.schedule.add(agent)
        self.assign_colors()
        #self.datacollector.collect(self)
        print("Made it")

    # TODO: do this for road segments as well
    def assign_colors(self):
        biker_values = []
        road_values = []
        max_bike_val = 0
        max_road_val = 0
        max_bike = None
        max_road = None
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
                        road_values.append(agent.heat_accumulation)
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
                # red_val = norm_bike(agent.heat_accumulation)
                # agent.color = (red_val, 0, 0, 1)
                if agent.heat_accumulation > top:
                    agent.color = cmap_bike(norm_bike(top))
                else:
                    agent.color = cmap_bike(norm_bike(agent.heat_accumulation))
            elif isinstance(agent, RoadAgent):
                if agent.heat_accumulation > top:
                    agent.color = cmap_road(norm_road(top))
                else:
                    agent.color = cmap_road(norm_road(agent.heat_accumulation))
                # blue_val = norm_road(agent.heat_accumulation)
                # agent.color = (0, 0, blue_val, 1)
                #agent.color = cmap_road(norm_road(agent.heat_accumulation))
        if max_bike and max_road:
            print("Geometry: " + str(max_bike.geometry) + " heat: " + str(max_bike.heat_accumulation))
            print("Geometry: " + str(max_road.geometry) + " heat: " + str(max_road.heat_accumulation))

    def reset_counts(self):
        self.counts = {
            "cool": 0,
            "warm": 0,
            "hot": 0,
            "burning": 0
        }

    def step(self):
        """Advance the model by one step."""
        # The model's step will go here for now this will call the step method of each agent and print the agent's unique_id
        self.steps += 1
        #self.reset_counts()
        self.schedule.step()
        #self.datacollector.collect(self)
        self.assign_colors()

        # TODO: set condition to stop running once all paths have been run


def get_cool_count(model):
    return model.counts["cool"]


def get_warm_count(model):
    return model.counts["warm"]


def get_hot_count(model):
    return model.counts["hot"]


def get_burning_count(model):
    return model.counts["burning"]
