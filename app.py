# app.py
from model import UrbanMoodModel
from mesa.visualization import Slider, SolaraViz, make_plot_component
from mesa.visualization.components.matplotlib_components import make_mpl_space_component


def agent_portrayal(agent):
    if agent.isolated:
        return {"color": "gray"}
    elif agent.mood > 0.5:
        return {"color": "green"}
    elif agent.mood < -0.5:
        return {"color": "red"}
    else:
        return {"color": "orange"}


def background_color(pos, layer):
    value = layer.get(pos, 0.0)
    if value > 0:
        return "#d0f0c0"  # green space
    elif value < 0:
        return "#f9c0c0"  # stress zone
    return "#ffffff"  # neutral


grid_component = make_mpl_space_component(
    UrbanMoodModel,
    agent_portrayal=agent_portrayal,
    property_layers={"mood_modifier": background_color},
    fps=3
)

plot_component = make_plot_component(
    UrbanMoodModel,
    title="Mood and Isolation Over Time",
    series=["average_mood", "num_isolated"]
)

page = SolaraViz(
    UrbanMoodModel,
    [grid_component, plot_component],
    name="UrbanMood",
    parameters={
        "width": Slider(10, 50, 30, name="Grid Width"),
        "height": Slider(10, 50, 30, name="Grid Height"),
        "N": Slider(10, 300, 100, name="Agents"),
        "green_pct": Slider(0.0, 0.5, 0.1, step=0.05, name="Green %"),
        "stress_pct": Slider(0.0, 0.5, 0.1, step=0.05, name="Stress %")
    }
)
