from model import UrbanMoodModel
from mesa.visualization import Slider, SolaraViz, make_plot_component
from mesa.visualization.components.matplotlib_components import make_mpl_space_component

def agent_portrayal(agent):
    """Visualization settings for agents"""
    if agent.isolated:
        return {"marker": "s", "color": "gray", "size": 15}
    return {
        "marker": "o",
        "color": "green" if agent.mood > 0 else "red",
        "size": 10 + abs(agent.mood)*30
    }

env_portrayal = {
    "environment": {
        "cmap": "RdYlGn",
        "vmin": -0.1,
        "vmax": 0.1,
        "alpha": 0.3,
        "colorbar": True
    }
}

mood_space = make_mpl_space_component(
    agent_portrayal=agent_portrayal,
    propertylayer_portrayal=env_portrayal,
    draw_grid=False
)

model_params = {
    "width": Slider("Grid Width", 10, 50, 30),
    "height": Slider("Grid Height", 10, 50, 30),
    "N": Slider("Agents", 10, 300, 100),
    "green_pct": Slider("Green %", 0.0, 0.5, 0.1, 0.05),
    "stress_pct": Slider("Stress %", 0.0, 0.5, 0.1, 0.05)
}

page = SolaraViz(
    UrbanMoodModel,
    components=[
        mood_space,
        make_plot_component("Average Mood"),
        make_plot_component("Number of Isolated")
    ],
    model_params=model_params,
    name="Urban Mood Dynamics",
    play_interval=500
)