from mesa import Model
from mesa.space import SingleGrid, PropertyLayer
from agents import UrbanAgent
import random
import mesa
import numpy as np

class SimpleScheduler:
    def __init__(self, model):
        self.model = model
        self.agents = []

    def add(self, agent):
        self.agents.append(agent)

    def step(self):
        random.shuffle(self.agents)
        for agent in self.agents:
            agent.step()

class UrbanMoodModel(Model):
    def __init__(self, width=20, height=20, density=0.5, green_ratio=0.1, stress_ratio=0.1, seed=42):
        super().__init__(seed=seed)
        self.width = width
        self.height = height
        env_layer = PropertyLayer("environment", width, height, default_value=0)
        self.grid = SingleGrid(width, height, torus=False, property_layers=env_layer)
        self.schedule = SimpleScheduler(self)
        self.environment_map = {}
        self.agent_count = int(width * height * density)
        random.seed(seed)

        self._init_environment(green_ratio, stress_ratio)
        self._init_agents()

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Average_Mood": self.get_average_mood,
                "Mood_StdDev": self.get_mood_std,
                "Num_Isolated": self.get_num_isolated
            }
        )

        self.running = True

    def _init_environment(self, green_ratio, stress_ratio):
        total_cells = self.width * self.height
        num_green = int(total_cells * green_ratio)
        num_stress = int(total_cells * stress_ratio)
        all_positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        random.shuffle(all_positions)
        green_cells = all_positions[:num_green]
        stress_cells = all_positions[num_green:num_green + num_stress]

        for pos in green_cells:
            self.environment_map[pos] = "green"   
            self.grid.properties["environment"].data[pos] = 1
        for pos in stress_cells:
            self.environment_map[pos] = "stress"
            self.grid.properties["environment"].data[pos] = -1

    def _init_agents(self):
        all_positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        random.shuffle(all_positions)
        spawn_positions = all_positions[:self.agent_count]

        for pos in spawn_positions:
            mood = random.uniform(-0.5, 0.5)
            sensitivity = random.uniform(0.2, 0.8)
            mobility_threshold = random.uniform(-0.3, 0.1)
            isolation_threshold = random.uniform(-0.9, -0.5)

            agent = UrbanAgent(
                model=self,
                pos=pos,
                mood=mood,
                sensitivity=sensitivity,
                mobility_threshold=mobility_threshold,
                isolation_threshold=isolation_threshold
            )
            self.grid.place_agent(agent, pos)
            self.schedule.add(agent)

    def _generate_environment_layer(self):
        return [
            [1 if self.environment_map.get((x, y)) == "green" else -1 if self.environment_map.get((x, y)) == "stress" else 0
             for x in range(self.width)]
            for y in range(self.height)
        ]

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        new_env_list = self._generate_environment_layer()
        new_env_array = np.array(new_env_list)   # <- 关键：转成 ndarray
        self.grid.properties["environment"].data = new_env_array

    def get_average_mood(self):
        moods = [agent.mood for agent in self.schedule.agents]
        return sum(moods) / len(moods) if moods else 0

    def get_mood_std(self):
        moods = [agent.mood for agent in self.schedule.agents]
        if not moods:
            return 0
        avg = sum(moods) / len(moods)
        return (sum((m - avg) ** 2 for m in moods) / len(moods)) ** 0.5

    def get_num_isolated(self):
        return sum(1 for agent in self.schedule.agents if agent.is_isolated)