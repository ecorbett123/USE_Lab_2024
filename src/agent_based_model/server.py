import mesa
import mesa_geo as mg
from agents import BikerAgent
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


# model_params = {
#     "pop_size": mesa.visualization.Slider("Population size", 30, 10, 100, 10),
#     "init_infected": mesa.visualization.Slider(
#         "Fraction initial infection", 0.2, 0.00, 1.0, 0.05
#     ),
#     "exposure_distance": mesa.visualization.Slider(
#         "Exposure distance", 500, 100, 1000, 100
#     ),
# }

G = ox.load_graphml(filepath="../ny_bike_graph.graphml")
model_params = {
    "dir_name": "/Users/emmacorbett/PycharmProjects/USE_Lab/data/Citibike/test",
    "G": G
}


def biker_draw(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = {}
    if agent.heat_accumulation < 5:
        portrayal["color"] = "Green"
    elif agent.heat_accumulation < 10:
        portrayal["color"] = "Blue"
    elif agent.heat_accumulation < 20:
        portrayal["color"] = "Red"
    else:
        portrayal["color"] = "Black"
    if isinstance(agent, BikerAgent):
        portrayal["radius"] = "1"
    return portrayal


biker_text = BikerText()
map_element = mg.visualization.MapModule(biker_draw)
biker_chart = mesa.visualization.ChartModule(
    [
        {"Label": "cool", "Color": "Green"},
        {"Label": "warm", "Color": "Blue"},
        {"Label": "hot", "Color": "Red"},
        {"Label": "burning", "Color": "Black"},
    ]
)

server = mesa.visualization.ModularServer(
    BikerModel,
    [map_element, biker_chart, biker_text],
    "Basic agent-based biker model",
    model_params
)
