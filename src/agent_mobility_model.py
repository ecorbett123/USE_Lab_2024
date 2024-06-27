import mesa
import os
import pandas as pd
import osmnx as ox
import seaborn as sns
import random as rnd

class BikerAgent(mesa.Agent):
    """An agent with fixed journey."""

    def __init__(self, unique_id, model, origin, destination, route):
        # Pass the parameters to the parent class.
        super().__init__(unique_id, model)

        # Create the agent's variable and set the initial values.
        self.origin = origin
        self.destination = destination
        self.route = route
        self.cur_time_step = 0
        self.heat_accumulation = 0

    def step(self):
        # Accumulate heat index based on their route
        if self.cur_time_step < len(self.route):
            # TODO: get heat exposure for segment between node cur time step and node cur time step + 1
            # TODO: create proper heat accumulation function based on how long you've already been in the sun contiguosly
            self.heat_accumulation += rnd.random()
        self.cur_time_step += 1


class BikerModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, dir_name, G):
        super().__init__()
        self.num_agents = 0
        self.schedule = mesa.time.RandomActivation(self)
        dirs = os.listdir(dir_name)

        for file in dirs:
            if file.endswith('.csv'):
                df = pd.read_csv(dir_name + "/" + file)
                for _, row in df.iterrows():
                    orig = ox.distance.nearest_nodes(G, X=row['start_lng'], Y=row['start_lat'])
                    dest = ox.distance.nearest_nodes(G, X=row['end_lng'], Y=row['end_lat'])
                    route = ox.shortest_path(G, orig, dest, weight="travel_time")
                    a = BikerAgent(self.num_agents, self, orig, dest, route)
                    self.num_agents += 1
                    self.schedule.add(a)

    def step(self):
        """Advance the model by one step."""
        # The model's step will go here for now this will call the step method of each agent and print the agent's unique_id
        self.schedule.step()

G = ox.load_graphml(filepath="./ny_bike_graph.graphml")
agent_model = BikerModel("/Users/emmacorbett/PycharmProjects/USE_Lab/data/Citibike/test", G)

for i in range(30):
    agent_model.step()


agent_wealth = [a.heat_accumulation for a in agent_model.schedule.agents]
# Create a histogram with seaborn
hist = sns.histplot(agent_wealth, discrete=True)
hist.set(title="Heat exposure distribution", xlabel="Heat Exposure", ylabel="Number of agents")
hist.plot()

#TODO: verify this works/the route they're taking makes sense
# TODO: create visualization
