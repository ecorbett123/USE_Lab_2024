import mesa_geo as mg
from shapely.geometry import Point


def get_heat_accumulation(edge_data, next_node_dict):

    t2_measurement = float(next_node_dict['t2'])
    # TODO: Make sure the unit is right for avg mph (length and miles and seconds, etc. all need to match up)
    if 'travel_time' in edge_data and edge_data['travel_time'] and edge_data['travel_time'] > 0:
        time = edge_data['travel_time']
    else:
        max_speed = 15 # average cyclist speed is about 10mph, e-bike about 20
        if 'speed_kph' in edge_data and edge_data['speed_kph'] and edge_data['speed_kph'] > 0:
            max_speed = edge_data['speed_kph']/3.6
        length = edge_data['length']  # returns length in meters
        time = length/max_speed

    return time * t2_measurement

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
        self.color = None
        self.G = G
        #self.isElectric = isElectric
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
        if self.route and self.cur_time_step + 1 < len(self.route):
            cur_node = self.route[self.cur_time_step]
            next_node =self.route[self.cur_time_step + 1]
            next_node_dict = self.G.nodes[next_node]
            edge_data = self.G.get_edge_data(cur_node, next_node)
            if len(edge_data) < 1:
                print("Error: no edge between nodes {} and {} for agent {}".format(str(cur_node), str(next_node), str(self.unique_id)))
            else:
                self.heat_accumulation += get_heat_accumulation(edge_data[0], next_node_dict)
                self.geometry = self.move_point(next_node_dict['x'], next_node_dict['y'])
        # cat = self.get_heat_category(self.heat_accumulation)
        # self.model.counts[cat] += 1
        self.cur_time_step += 1

    def get_heat_category(self, heat_accumulation):
        if heat_accumulation < 50:
            return "cool"
        elif heat_accumulation < 100:
            return "warm"
        elif heat_accumulation < 200:
            return "hot"
        return "burning"


# TODO: could use this for visualization to indicate how much a segment has contributed to heat accumulation per agent !! This is what i should do next
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


class RoadAgent(mg.GeoAgent):
    """Neighbourhood agent. Changes color according to number of infected inside it."""

    def __init__(
        self, unique_id, model, geometry, crs, heat_contribution, edge_id):
        """
        Create a new Neighbourhood agent.
        :param unique_id:   Unique identifier for the agent
        :param model:       Model in which the agent runs
        :param geometry:    Shape object for the agent
        :param hotspot_threshold:   Number of infected agents in region
                                    to be considered a hot-spot
        """
        super().__init__(unique_id, model, geometry, crs)
        # self.get_heat_contribution()
        self.edge_id = edge_id
        self.cur_time_step = 0
        self.heat_contribution = heat_contribution
        self.heat_accumulation = 0
        self.color = None

    def step(self):
        """Advance agent one step."""
        self.get_heat_contribution()
        self.cur_time_step += 1

    # currently accumulates the raw number of bikers who used this path
    # eventually want to come up with some formula to include length of path to determine heat contribution
    def get_heat_contribution(self):
        neighbors = self.model.space.get_intersecting_agents(self)
        num_neigh = [neigh for neigh in neighbors if isinstance(neigh, BikerAgent)]
        self.heat_accumulation += (len(num_neigh) * self.heat_contribution)
        # self.heat_accumulation += self.heat_contribution

    def __repr__(self):
        return "Road segment " + str(self.unique_id)