import mesa
import mesa_geo as mg
from agents import BikerAgent, RoadAgent
from model import BikerModel
import osmnx as ox


class BikerText(mesa.visualization.TextElement):
    """
    Display a text count of how many steps have been taken
    """

    def __init__(self):
        pass

    def render(self, model):
        return "Steps: " + str(model.steps)


G = ox.load_graphml(filepath="/Users/emmacorbett/PycharmProjects/USE_Lab/src/agent_based_model/ny_bike_graph_heat_included_2.graphml")
model_params = {
    "dir_name": "/Users/emmacorbett/PycharmProjects/USE_Lab/data/Citibike/5_May_2024",
    "G": G
}


def biker_draw(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = {}
    color = [int(c * 255) for c in agent.color[:3]]
    portrayal["color"] = "rgb(" + str(color[0]) + "," + str(color[1]) + "," + str(color[2]) + ")"

    if isinstance(agent, RoadAgent):
        portrayal["radius"] = "0.5"
        portrayal["Shape"] = "line"

    if isinstance(agent, BikerAgent):
        portrayal["Shape"] = "circle"
        portrayal["Filled"] = "true"
        portrayal["radius"] = 3.0
    return portrayal


biker_text = BikerText()
map_element = mg.visualization.MapModule(biker_draw)

server = mesa.visualization.ModularServer(
    BikerModel,
    [map_element, biker_text],
    "Basic agent-based biker model",
    model_params
)
