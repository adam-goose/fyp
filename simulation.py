import random
from agent import Agent
from config import simulation_config

# Returns list of randomly generated agents
def spawn_agents():
    return [
        Agent(
            position=[
                random.uniform(*simulation_config["position_bounds"]),  # Random x
                random.uniform(*simulation_config["position_bounds"]),  # Random y
                random.uniform(*simulation_config["position_bounds"])  # Random z
            ],
            direction=[
                random.uniform(*simulation_config["direction_bounds"]),  # Random x direction
                random.uniform(*simulation_config["direction_bounds"]),  # Random y direction
                random.uniform(*simulation_config["direction_bounds"])  # Random z direction
            ],
            speed=random.uniform(*simulation_config["speed_bounds"])  # Random speed
        )
        for _ in range(simulation_config["num_agents"])
    ]