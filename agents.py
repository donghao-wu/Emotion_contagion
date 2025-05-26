from mesa import Agent  #

class UrbanAgent(Agent):  
    def __init__(self, unique_id, model, pos, mood, sensitivity, mobility_threshold, isolation_threshold):
        Agent.__init__(self, unique_id, model)  
        self.pos = pos
        self.mood = mood
        self.sensitivity = sensitivity
        self.mobility_threshold = mobility_threshold
        self.isolation_threshold = isolation_threshold
        self.is_isolated = False

    def step(self):
        if self.is_isolated:
            self.recover_mood()
        else:
            self.update_mood_from_neighbors()
            self.update_mood_from_environment()
            self.check_isolation()
            if not self.is_isolated:
                self.maybe_move()

    def update_mood_from_neighbors(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        if not neighbors:
            return
        neighbor_moods = [agent.mood for agent in neighbors if hasattr(agent, 'mood')]
        if neighbor_moods:
            avg_mood = sum(neighbor_moods) / len(neighbor_moods)
            self.mood += (avg_mood - self.mood) * self.sensitivity

    def update_mood_from_environment(self):
        env_type = self.model.environment_map.get(self.pos, "neutral")
        if env_type == "green":
            self.mood += 0.1
        elif env_type == "stress":
            self.mood -= 0.1

    def check_isolation(self):
        if self.mood < self.dynamic_isolation_threshold():
            self.is_isolated = True

    def recover_mood(self):
        self.mood += 0.02
        if self.mood >= self.mobility_threshold:
            self.is_isolated = False

    def maybe_move(self):
        if self.model.grid:
            move_prob = max(0.0, min(1.0, self.mood - self.mobility_threshold + 0.5))
            if self.model.random.random() < move_prob:
                possible_moves = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
                empty_cells = [cell for cell in possible_moves if self.model.grid.is_cell_empty(cell)]
                if empty_cells:
                    new_pos = self.model.random.choice(empty_cells)
                    self.model.grid.move_agent(self, new_pos)
                    self.pos = new_pos

    def dynamic_isolation_threshold(self):
        env_type = self.model.environment_map.get(self.pos, "neutral")
        modifier = -0.1 if env_type == "green" else 0.1 if env_type == "stress" else 0
        return self.isolation_threshold + modifier
