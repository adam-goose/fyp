import simulation
from simulation import *

# Initialise the Ursina app
app = Ursina()

last_time = time.time()

# Initialize agents
agents = spawn_agents()

# Create an Ursina Entity for each agent and store in a list
agent_entities = [Entity(model="sphere", color=color.random_color(), scale=simulation_config["agent_scale"], position=agent.position) for agent in agents]

boundary = simulation.create_boundary()
simulation.set_camera()

def update():
    global last_time
    current_time = time.time()
    elapsed_time = current_time - last_time

    if elapsed_time < frame_duration:
        time.sleep(frame_duration - elapsed_time)  # Sleep to maintain 30 FPS

    # Update simulation logic and render positions
    for agent, agent_entity in zip(agents, agent_entities):
        agent.update_position()  # Update agent logic

        agent_entity.position = agent.position  # Sync visual position with logic

    last_time = time.time()

# Run the Ursina app
app.run()