from vpython import sphere, vector, rate, canvas
from agent import Agent
from config import simulation_config
import numpy as np

# Create a standalove VPython window
scene = canvas(title="Swarm Simulation",
               width=800, height=600,
               center=vector(0, 0, 0), backgroudn=vector(0.2, 0.2, 0.2))

# Initialize agents
agents = [
    Agent(position=[0, 1, 0], direction=[1.2, 0, 0], speed=1.0),
    Agent(position=[2, 2, 1], direction=[0, 1.4, 0], speed=1.0),
    Agent(position=[3, 3, 0], direction=[-0.1, 0.5, 0], speed=1.0)
]

# Initialise VPython spheres for agents
vpython_spheres = [sphere(pos=vector(agent.position[0], agent.position[1], agent.position[2]),
                          radius=0.5, color=vector(0, 1, 0)) for agent in agents]


# Simulation parameters
num_frames = 20

# Simulation loop
for frame in range(num_frames):
    print(f"Frame {frame + 1}")
    for i, agent in enumerate(agents):
        # Update the agent's position and direction
        agent.update_position()

        vpython_spheres[i].pos = vector(agent.position[0], agent.position[1], agent.position[2])

    rate(2) # Frame rate of simulation

# Keep the VPython window open after the simulation ends
print("Simulation complete. The window will remain open.")
while True:
    rate(30)  # This keeps the window responsive