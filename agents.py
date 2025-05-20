from mesa import Agent
import math

class UrbanAgent(Agent):
    """
    An agent that holds a mood state, moves around, and interacts emotionally with neighbors.
    """
    def __init__(self, unique_id, model, mood=0.0, sensitivity=0.5):
        super().__init__(unique_id, model)
        self.mood = mood  # [-1, 1]
        self.sensitivity = sensitivity  # how much mood changes based on neighbors
        self.isolated = False #initial state of isolation will be false
        # Randomly set thresholds for mobility and isolation
        self.mobility_threshold = self.random.uniform(-0.4, 0.0)
        self.isolation_threshold = self.random.uniform(-0.9, -0.6)

    def step(self):
        if self.isolated:
            self.recover()
        else:
            self.update_mood()
            self.check_isolation()
            self.move()

    def update_mood(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        neighbor_moods = [a.mood for a in neighbors if isinstance(a, UrbanAgent)]

        # This is a simplified version of mood change, we can change it to interacti with each neightbor then
        # update the mood based on the differences
        if neighbor_moods:
            avg_neighbor_mood = sum(neighbor_moods) / len(neighbor_moods)
            delta = self.sensitivity * (avg_neighbor_mood - self.mood)
            self.mood += delta

        # Apply environment-based modifier
        modifier = self.model.environment_layer.get(self.pos, 0.0)
        self.mood += modifier

        # Clamp mood
        self.mood = max(-1, min(1, self.mood))

    def check_isolation(self):
        threshold = self.isolation_threshold
        if self.model.environment_layer.get(self.pos, 0) > 0:  # green space
            threshold -= 0.1  # more forgiving in positive space

        if self.mood < threshold:
            self.isolated = True

    def recover(self):
        self.mood = min(1.0, self.mood + 0.02)
        if self.mood > -0.5:
            self.isolated = False

    def move(self):
        if self.random.random() > self.movement_probability():
            return

        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        empty = [pos for pos in possible_steps if self.model.grid.is_cell_empty(pos)]
        if empty:
            new_pos = self.random.choice(empty)
            self.model.grid.move_agent(self, new_pos)

    def movement_probability(self):
        """Smooth transition: sigmoid probability of moving based on mood vs mobility threshold"""
        k = 10  # sensitivity of the sigmoid
        x = self.mood - self.mobility_threshold
        return 1 / (1 + math.exp(-k * x))