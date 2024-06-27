import mesa_geo as mg
import random as rnd
from shapely.geometry import Point

class BikerAgent(mg.GeoAgent):
    """An agent with fixed journey."""

    def __init__(self, unique_id, model, geometry, crs, origin, destination, route, G):
        '''
        Create a new traveler agent.
        :param unique_id: Unique id for agent
        :param model: Model the agents run in
        :param geometry: Shape object for the agent
        :param origin: Origin of their journey
        :param destination: Destination of their journey
        :param route: Shortest path route between their origin and destination
        '''
        super().__init__(unique_id, model, geometry, crs)

        # Create the agent's variable and set the initial values.
        self.origin = origin
        self.destination = destination
        self.route = route
        self.cur_time_step = 0
        self.heat_accumulation = 0
        self.G = G

        self.model.counts["cool"] += 1

    def move_point(self, x, y):
        """
        Move a point by creating a new one
        :param x:  New lat coordinate to move to
        :param y:  New long coordinate to move to
        """
        return Point(x, y)

    def step(self):
        # Accumulate heat index based on their route
        if self.cur_time_step < len(self.route):
            # TODO: get heat exposure for segment between node cur time step and node cur time step + 1
            # TODO: create proper heat accumulation function based on how long you've already been in the sun continuously
            self.heat_accumulation += rnd.random()
            self.geometry = self.move_point(self.G.nodes[self.route[self.cur_time_step]]['x'], self.G.nodes[self.route[self.cur_time_step]]['y'])
        cat = self.get_heat_category(self.heat_accumulation)
        self.model.counts[cat] += 1
        self.cur_time_step += 1

    def get_heat_category(self, heat_accumulation):
        if heat_accumulation < 5:
            return "cool"
        elif heat_accumulation < 10:
            return "warm"
        elif heat_accumulation < 20:
            return "hot"
        return "burning"


# TODO: could use this for visualization to indicate how much a segment has contributed to heat accumulation per agent !!
class NeighbourhoodAgent(mg.GeoAgent):
    """Neighbourhood agent. Changes color according to number of infected inside it."""

    def __init__(
        self, unique_id, model, geometry, crs):
        """
        Create a new Neighbourhood agent.
        :param unique_id:   Unique identifier for the agent
        :param model:       Model in which the agent runs
        :param geometry:    Shape object for the agent
        :param hotspot_threshold:   Number of infected agents in region
                                    to be considered a hot-spot
        """
        super().__init__(unique_id, model, geometry, crs)
        self.color_hotspot()
        self.heat_accumulation = 0

    def step(self):
        """Advance agent one step."""
        self.color_hotspot()

    def color_hotspot(self):
        # Decide if this region agent is a hot-spot
        # (if more than threshold person agents are infected)
        neighbors = self.model.space.get_intersecting_agents(self)
        hot_neighbors = [
            neighbor.heat_accumulation for neighbor in neighbors if neighbor.heat_accumulation > 5
        ]
        if len(hot_neighbors) > 0:
            self.heat_accumulation = sum(hot_neighbors) / len(hot_neighbors) # avg heat accumulation
            # this will need to be changed!!

    def __repr__(self):
        return "Neighborhood " + str(self.unique_id)