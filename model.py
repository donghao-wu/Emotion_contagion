from mesa import Model
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
from agents import UrbanAgent
import random

## define the scheduler for the model
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
    def __init__(self, width=20, height=20, density = 0.5, green_ratio = 0.1, stress_ratio = 0.1 , seed = 42):
        """
        Initialize the UrbanMood model.
        
        Parameters:
        - width, height: Grid dimensions
        - density: Proportion of cells that will be occupied by agents
        - green_ratio: Ratio of green zones (positive mood effect)
        - stress_ratio: Ratio of stress zones (negative mood effect)
        - seed: Random seed for reproducibility
        """
        super().__init__(seed=seed)
        self.width = width
        self.height = height
        self.grid = SingleGrid(width, height, torus =False)
        self.schedule = SimpleScheduler(self)
        self.environment_map = {}
        self.agent_count = int(width * height * density)
        self._init_environment(green_ratio, stress_ratio)
        self._init_agents()
        random.seed(seed)
        self.datacollector = DataCollector(
            model_reporters={
                "Average_Mood": self.get_average_mood,
                "Mood_StdDev": self.get_mood_std,
                "Num_Isolated": self.get_num_isolated
            }
        )
        self.running = True

    # Initialize the environment with green and stress zones
    def _init_environment(self, green_ratio, stress_ratio):
        """
        Randomly assign environment modifiers to grid cells.
        """
        total_cells = self.width * self.height
        num_green = int(total_cells * green_ratio)
        num_stress = int(total_cells * stress_ratio)

        all_positions = [(x, y) for x in range(self.width) for y in range(self.height)]
        random.shuffle(all_positions)

        green_cells = all_positions[:num_green]
        stress_cells = all_positions[num_green:num_green + num_stress]

        for pos in green_cells:
            self.environment_map[pos] = "green"
        for pos in stress_cells:
            self.environment_map[pos] = "stress"
        # Remaining are neutral by default

    # Initialize agents with random positions and moods
    def _init_agents(self):
        """
        Place agents on the grid with initialized properties.
        """
        agent_id = 0
        for x in range(self.width):
            for y in range(self.height):
                if agent_id >= self.agent_count:
                    return

                if self.grid.is_cell_empty((x, y)):
                    mood = random.uniform(-0.2, 0.2)
                    sensitivity = random.uniform(0.2, 0.8)
                    mobility_threshold = random.uniform(-0.3, 0.1)
                    isolation_threshold = random.uniform(-0.9, -0.5)

                    agent = UrbanAgent(
                        model=self,
                        pos=(x, y),
                        mood=mood,
                        sensitivity=sensitivity,
                        mobility_threshold=mobility_threshold,
                        isolation_threshold=isolation_threshold
                    )

                    self.grid.place_agent(agent, (x, y))
                    self.schedule.add(agent)
                    agent_id += 1
    def step(self):
        """
        Advance model by one tick: each agent updates, and data is collected.
        """
        self.schedule.step()
        self.datacollector.collect(self)
    
    # Data collection methods
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