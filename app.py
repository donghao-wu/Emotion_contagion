from model import UrbanMoodModel
from mesa.visualization import (
    SolaraViz,
    Slider,
    make_plot_component,
    make_space_component
)

# --- Agent Visual Representation ---
def agent_portrayal(agent):
    mood = agent.mood
    if agent.is_isolated:
        color = "#cccccc"
    elif mood > 0.2:
        color = "#55cc55"
    elif mood < -0.2:
        color = "#cc5555"
    else:
        color = "#bbbbbb"

    return {
        "color": color,
        "marker": "o",
        "size": 25,
    }

# --- GUI Parameters ---
model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    },
    "width": Slider("Grid Width", value=20, min=10, max=50, step=1),
    "height": Slider("Grid Height", value=20, min=10, max=50, step=1),
    "density": Slider("Population Density", value=0.7, min=0.1, max=1.0, step=0.05),
    "green_ratio": Slider("Green Space Ratio", value=0.1, min=0.0, max=0.5, step=0.01),
    "stress_ratio": Slider("Stress Zone Ratio", value=0.1, min=0.0, max=0.5, step=0.01),
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Random Seed",
    }
}

# --- Visualization Components ---
Space = make_space_component(agent_portrayal=agent_portrayal)
MoodPlot = make_plot_component("Average_Mood")
IsolationPlot = make_plot_component("Num_Isolated")

model = UrbanMoodModel()
page = SolaraViz(
    model,
    components=[Space, MoodPlot, IsolationPlot],
    model_params=model_params,
    name="UrbanMood: Emotion Contagion in Cities",
    play_interval=300,
)

page
