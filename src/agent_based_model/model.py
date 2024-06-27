import mesa
import os
import pandas as pd
import osmnx as ox
from agents import BikerAgent, NeighbourhoodAgent
import mesa_geo as mg
from shapely.geometry import Point

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
        self.datacollector = mesa.DataCollector(
            {
                "cool": get_cool_count,
                "warm": get_warm_count,
                "hot": get_hot_count,
                "burning": get_burning_count,
            }
        )

        # Set up the Neighborhood regions:
        ac = mg.AgentCreator(NeighbourhoodAgent, model=self)
        neighbourhood_agents = ac.from_file(
            self.geojson_regions, unique_id=self.unique_id
        )
        self.space.add_agents(neighbourhood_agents)
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
                for _, row in df.iterrows():
                    orig = ox.distance.nearest_nodes(G, X=row['start_lng'], Y=row['start_lat'])
                    dest = ox.distance.nearest_nodes(G, X=row['end_lng'], Y=row['end_lat'])
                    route = ox.shortest_path(G, orig, dest, weight="travel_time")
                    x, y = self.G.nodes[orig]['x'], self.G.nodes[orig]['y']

                    a = ac_population.create_agent(Point(x, y), self.num_agents)
                    a.route = route
                    self.num_agents += 1
                    self.space.add_agents(a)
                    self.schedule.add(a)

        for agent in neighbourhood_agents:
            self.schedule.add(agent)

        self.datacollector.collect(self)

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
        self.reset_counts()
        self.schedule.step()
        self.datacollector.collect(self)

        # TODO: set condition to stop running once all paths have been run


def get_cool_count(model):
    return model.counts["cool"]


def get_warm_count(model):
    return model.counts["warm"]


def get_hot_count(model):
    return model.counts["hot"]


def get_burning_count(model):
    return model.counts["burning"]
