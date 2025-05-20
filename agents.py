from mesa.experimental.cell_space import CellAgent
import math
import numpy as np

class UrbanAgent(CellAgent):
    """Agent with emotional state and mobility behaviors"""
    
    def __init__(self, model, cell, sensitivity=0.5):
        super().__init__(model)
        self.cell = cell
        self.mood = model.random.uniform(-0.2, 0.2)
        self.sensitivity = sensitivity
        self.isolated = False
        self.mobility_threshold = model.random.uniform(-0.4, 0.0)
        self.isolation_threshold = model.random.uniform(-0.9, -0.6)

    @classmethod
    def create_agents(cls, model, n, cells, **kwargs):
        """Batch create agents with distributed parameters"""
        for i in range(n):
            agent_params = {k: v[i] for k, v in kwargs.items()}
            agent = cls(model, cells[i], **agent_params)
            model.grid.place_agent(agent, cells[i])
            model.schedule.add(agent)

    def perceive_environment(self):
        """Process environmental effects"""
        env_value = self.cell.environment
        if env_value > 0:  # Green space
            self.mood += 0.1
        elif env_value < 0:  # Stress zone
            self.mood -= 0.1
        self.mood = np.clip(self.mood, -1, 1)

    def update_mood(self):
        """Social contagion mechanism"""
        if self.isolated:
            self.mood = min(self.mood + 0.02, 0)
            return
            
        neighbors = self.cell.get_neighbors()
        if neighbors:
            avg_mood = np.mean([a.mood for a in neighbors if isinstance(a, UrbanAgent)])
            delta = self.sensitivity * (avg_mood - self.mood)
            self.mood += delta

    def check_isolation(self):
        """Update isolation status"""
        current_threshold = self.isolation_threshold
        if self.cell.environment > 0:  # Green space
            current_threshold -= 0.1
            
        if self.mood < current_threshold:
            self.isolated = True
        elif self.mood > -0.5:
            self.isolated = False

    def move_decision(self):
        """Movement logic"""
        if self.isolated or self.random.random() > self._movement_prob():
            return
            
        candidates = [
            cell for cell in self.cell.get_neighborhood(1)
            if cell.is_empty and cell.environment >= self.cell.environment
        ]
        if candidates:
            self.cell = self.random.choice(candidates)

    def _movement_prob(self):
        """Sigmoid probability calculation"""
        k = 10
        x = self.mood - self.mobility_threshold
        return 1 / (1 + math.exp(-k * x))