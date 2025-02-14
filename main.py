import simulation
from simulation import *
from config import *
from ursina import *
from settings_ui import *


# Initialise the Ursina app
app = Ursina()

last_time = time.time()

# Initialize agents
agents = spawn_agents()

# Create an Ursina Entity for each agent and store in a list
agent_entities = [Entity(model="sphere", color=color.blue, scale=simulation_config["agent_scale"], position=agent.position) for agent in agents]

boundary = simulation.create_boundary()
simulation.set_camera()

def update():
    global last_time
    current_time = time.time()
    elapsed_time = current_time - last_time

    if elapsed_time < frame_duration:
        time.sleep(frame_duration - elapsed_time)  # Sleep to maintain 30 FPS

    if agents:
        avg_speed = sum(agent.speed for agent in agents) / len(agents)
        speed_readout.text = f"Avg Speed: {avg_speed:.2f}"

    # Update simulation logic and render positions
    for agent, agent_entity in zip(agents, agent_entities):
        agent.update_position()  # Update agent logic

        agent_entity.position = agent.position  # Sync visual position with logic

    last_time = time.time()

# Window
window.size = (1400, 1000)
window.borderless = False

speed_readout = Text(text="Avg Speed: 0.0", position=(-0.7, 0.4), scale=2, color=color.white)

# Create the settings UI and get the containers.
ui_elements = create_settings_ui()
background_dimmer = ui_elements['background_dimmer']
physics_ui = ui_elements['physics_ui']
simulation_ui = ui_elements['simulation_ui']
agents_ui = ui_elements['agents_ui']
settings_containers = ui_elements['settings_containers']

# Create buttons to toggle each settings UI.
physics_button = Button(text="Physics", parent=camera.ui,
                        position=(-0.7, 0.4), scale=(0.2, 0.05))
physics_button.on_click = lambda: toggle_settings(physics_ui, background_dimmer, settings_containers)

simulation_button = Button(text="Simulation", parent=camera.ui,
                           position=(-0.7, 0.3), scale=(0.2, 0.05))
simulation_button.on_click = lambda: toggle_settings(simulation_ui, background_dimmer, settings_containers)

agent_button = Button(text="Agent", parent=camera.ui,
                      position=(-0.7, 0.2), scale=(0.2, 0.05))
agent_button.on_click = lambda: toggle_settings(agents_ui, background_dimmer, settings_containers)

# Run the Ursina app
app.run()