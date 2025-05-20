# model.py
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.experimental.space import OrthogonalVonNeumannGrid
from mesa.experimental.components import PropertyLayer
from agents import UrbanAgent
import numpy as np
import random


class UrbanMoodModel(Model):
    def __init__(self, width=30, height=30, N=100, green_pct=0.1, stress_pct=0.1):
        self.grid = OrthogonalVonNeumannGrid(width, height, torus=True)
        self.schedule = RandomActivation(self)
        self.environment_layer = PropertyLayer("mood_modifier", self.grid)

        self.num_agents = N
        self.green_pct = green_pct
        self.stress_pct = stress_pct

        self._init_environment()
        self._init_agents()

        self.datacollector = []

    def _init_environment(self):
        """Assign green space (+0.1) and stress zones (-0.1) to the environment layer."""
        all_positions = [(x, y) for x in range(self.grid.width) for y in range(self.grid.height)]
        random.shuffle(all_positions)
        total_cells = len(all_positions)
        green_count = int(self.green_pct * total_cells)
        stress_count = int(self.stress_pct * total_cells)

        green_cells = all_positions[:green_count]
        stress_cells = all_positions[green_count:green_count + stress_count]
        neutral_cells = all_positions[green_count + stress_count:]

        for pos in green_cells:
            self.environment_layer.set(pos, 0.1)
        for pos in stress_cells:
            self.environment_layer.set(pos, -0.1)
        for pos in neutral_cells:
            self.environment_layer.set(pos, 0.0)

    def _init_agents(self):
        """Create agents with randomized mood and sensitivity."""
        for i in range(self.num_agents):
            mood = random.uniform(-0.2, 0.2)
            sensitivity = random.uniform(0.2, 0.8)
            agent = UrbanAgent(i, self, mood=mood, sensitivity=sensitivity)
            self.grid.place_agent(agent, self.grid.find_empty())
            self.schedule.add(agent)

    def step(self):
        self.schedule.step()
        self.datacollector.append(self.collect_data())

    def collect_data(self):
        moods = [agent.mood for agent in self.schedule.agents]
        isolates = sum(agent.isolated for agent in self.schedule.agents)
        return {
            "average_mood": np.mean(moods),
            "num_isolated": isolates
        }
