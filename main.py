from agent import Agent
from config import simulation_config
import numpy as np

# Initialize agents
agents = [
    Agent(position=[0, 1, 0], direction=[1.2, 0, 0], speed=1.0),
    Agent(position=[2, 2, 1], direction=[0, 1.4, 0], speed=1.0),
    Agent(position=[3, 3, 0], direction=[-0.1, 0.5, 0], speed=1.0)
]

# Simulation parameters
num_frames = 15

# Simulation loop
for frame in range(num_frames):
    print(f"Frame {frame + 1}")
    for agent in agents:
        # Update the agent's position and direction
        agent.update_position()

        # Print the agent's state
        print(f"Agent Position: {agent.position}, Direction: {agent.direction}")

    print("\n")  # Separate frames for readability
