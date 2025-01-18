from ursina import *
from agent import Agent
from config import simulation_config
import numpy as np

# Initialise the Ursina app
app = Ursina()

# Initialize agents
agents = [
    Agent(position=[0, 1, 0], direction=[1.2, 0, 0], speed=1.0),
    Agent(position=[2, 2, 1], direction=[0, 1.4, 0], speed=1.0),
    Agent(position=[3, 3, 0], direction=[-0.1, 0.5, 0], speed=1.0),
    Agent(position=[0, 2, 0], direction=[1.2, 0, 0], speed=1.0),
    Agent(position=[2, 3, 1], direction=[0, 1.4, 0], speed=1.0),
    Agent(position=[3, 3, 4], direction=[-0.1, 0.5, 0], speed=1.0),
    Agent(position=[0, 1, 4], direction=[1.2, 0, 0], speed=1.0),
    Agent(position=[3, 2, 1], direction=[0, 1.4, 0], speed=1.0),
    Agent(position=[3, 4, 0], direction=[-0.1, 0.5, 0], speed=1.0)
]

# Create an Ursina Entity for each agent and store in a list
agent_entities = [Entity(model="sphere", color=color.random_color(), scale=0.2, position=agent.position) for agent in agents]

# Define camera position and direction
camera.position = (25,20, -70)  # Adjust as needed
camera.look_at((0, 0, 0))  # Ensure the camera looks at the center of the scene

boundary = Entity(model=Mesh(vertices=[Vec3(-10, -10, -10), Vec3(10, -10, -10), Vec3(10, 10, -10), Vec3(-10, 10, -10),
                                     Vec3(-10, -10, 10), Vec3(10, -10, 10), Vec3(10, 10, 10), Vec3(-10, 10, 10)],
                            triangles=[(0,1,2), (0,2,3), (4,5,6), (4,6,7), (0,1,5), (0,5,4), (1,2,6), (1,6,5),
                                       (2,3,7), (2,7,6), (3,0,4), (3,4,7)], mode='line'), color=color.white)


# Frame timing setup
frame_duration = 1 / 30  # 30 FPS

last_time = time.time()

def update():
    global last_time
    current_time = time.time()
    elapsed_time = current_time - last_time

    if elapsed_time < frame_duration:
        time.sleep(frame_duration - elapsed_time)  # Sleep to maintain 30 FPS

    # Update simulation logic and render positions
    for agent, entity in zip(agents, agent_entities):
        agent.update_position()  # Update agent logic

        # Constrain positions within boundaries (example: -10 to 10 in all axes)
        agent.position[0] = max(min(agent.position[0], 10), -10)
        agent.position[1] = max(min(agent.position[1], 10), -10)
        agent.position[2] = max(min(agent.position[2], 10), -10)

        entity.position = agent.position  # Sync visual position with logic

    last_time = time.time()

# Run the Ursina app
app.run()
