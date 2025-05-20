from mesa import Model
from mesa.time import RandomActivation
from mesa.experimental.cell_space import OrthogonalVonNeumannGrid
from mesa.experimental.cell_space.property_layer import PropertyLayer
import numpy as np

class UrbanMoodModel(Model):
    """Core model implementing urban emotion dynamics"""
    
    def __init__(
        self,
        width=30,
        height=30,
        N=100,
        green_pct=0.1,
        stress_pct=0.1,
        seed=None
    ):
        super().__init__(seed=seed)
        self.grid = OrthogonalVonNeumannGrid((width, height), torus=True, random=self.random)
        self.schedule = RandomActivation(self)
        
        # Initialize environment layer
        self._init_environment(green_pct, stress_pct)
        
        # Create agents
        UrbanAgent.create_agents(
            self,
            N,
            self.random.choices(self.grid.all_cells.cells, k=N),
            sensitivity=self.rng.uniform(0.2, 0.8, N)
        )
        
        # Configure data collection
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "average_mood": lambda m: np.mean([a.mood for a in m.schedule.agents]),
                "num_isolated": lambda m: sum(a.isolated for a in m.schedule.agents)
            }
        )

    def _init_environment(self, green_pct, stress_pct):
        """Initialize environmental modifiers"""
        env_data = np.zeros((self.grid.width, self.grid.height))
        total_cells = self.grid.width * self.grid.height
        
        # Assign green zones
        green_cells = int(total_cells * green_pct)
        env_data.flat[self.random.choice(total_cells, green_cells, replace=False)] = 0.1
        
        # Assign stress zones
        stress_cells = int(total_cells * stress_pct)
        env_data.flat[self.random.choice(total_cells, stress_cells, replace=False)] = -0.1
        
        self.grid.add_property_layer(
            PropertyLayer.from_data("environment", env_data)
        )

    def step(self):
        """Advance model by one step"""
        self.schedule.step()
        self.datacollector.collect(self)