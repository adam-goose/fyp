import simulation
from simulation import *
from config import *
from ursina import *
from settings_ui import *
from config import default_simulation_config


# Initialise the Ursina app
app = Ursina()

last_time = time.time()

# Initialize agents
agents = spawn_agents()

auto_rotate_enabled = False
orbit_angle = 0


# Create an Ursina Entity for each agent and store in a list
# DEBUGGING - MAKES THE FIRST AGENT RED, SECOND GREEN, AND THIRD YELLOW
agent_entities = [
    Entity(
        model="cube",
        color=(
            color.red if i == 0
            else color.green if i == 1
            else color.yellow if i == 2
            else color.blue
        ),
        scale=simulation_config["agent_scale"],
        position=agent.position
    )
    for i, agent in enumerate(agents)
]

boundary = simulation.create_boundary()
simulation.set_camera()

def update():
    global last_time
    global orbit_angle
    current_time = time.time()
    elapsed_time = current_time - last_time


    if auto_rotate_enabled:
        orbit_angle += simulation_config["camera_orbit_speed"] * time.dt

        cam_x = orbit_radius * math.cos(orbit_angle)
        cam_z = orbit_radius * math.sin(orbit_angle)
        cam_y = orbit_height  # direct from user config at toggle time

        camera.position = Vec3(cam_x, cam_y, cam_z)
    else:
        camera.position = simulation_config["camera_position"]

    camera.look_at(simulation_config["camera_look_at"])
    camera.rotation_z = 0  # Force no roll

    if elapsed_time < frame_duration:
        time.sleep(frame_duration - elapsed_time)  # Sleep to maintain 30 FPS

    if agents:
        avg_speed = sum(agent.speed for agent in agents) / len(agents)
        #speed_readout.text = f"Avg Speed: {avg_speed:.2f}"

        #first_agent_speed = agents[0].speed
        #first_agent_speed_readout.text = f"First Agent Speed: {first_agent_speed:.2f}"
        #second_agent_speed_readout.text = f"Second Agent Speed: {agents[1].speed:.2f}"
        #third_agent_speed_readout.text = f"Third Agent Speed: {agents[2].speed:.2f}"

    # Update simulation logic and render positions
    for agent, agent_entity in zip(agents, agent_entities):
        agent.update_position()  # Update agent logic

        agent_entity.position = agent.position  # Sync visual position with logic

    last_time = time.time()

def toggle_auto_rotate():
    global auto_rotate_enabled, orbit_angle, orbit_radius, orbit_height

    auto_rotate_enabled = not auto_rotate_enabled

    if auto_rotate_enabled:
        orbit_angle = 0

        # Use the user's configured camera position
        pos = simulation_config["camera_position"]
        orbit_radius = math.sqrt(pos[0] ** 2 + pos[2] ** 2)
        orbit_height = pos[1]

        if orbit_radius < 0.01:
            orbit_radius = 10  # fallback if they're dead center


def reset_boundaries():
    global boundary

    # Destroy current boundary
    if boundary:
        destroy(boundary)

    # Recreate boundary using current config
    boundary = simulation.create_boundary()


def reset_simulation():
    global agents, agent_entities, boundary

    # Destroy current agent entities
    for ent in agent_entities:
        destroy(ent)

    # Destroy the current boundary
    destroy(boundary)

    color_mode = simulation_config["agent_colour_mode"]

    # Recreate agents and their visual entities
    agents = spawn_agents()
    agent_entities = [
        Entity(
            model="cube",
            color=agent.color,  # ← use the color set in spawn_agents
            scale=simulation_config["agent_scale"],
            position=agent.position
        )
        for agent in agents
    ]

    # Recreate boundary and camera
    boundary = simulation.create_boundary()
    simulation.set_camera()

def reset_simulation_to_default():
    # Overwrite current config with defaults
    for key, value in default_simulation_config.items():
        simulation_config[key] = value

    # Optionally: update slider values to reflect reset (if you want the UI to reflect it visually)
    # Update slider visuals to reflect default values
    for container in settings_containers:
        for child in container.children:
            if isinstance(child, Slider) and hasattr(child, 'key'):
                if '[' in child.key and ']' in child.key:
                    base_key, index = child.key.split('[')
                    index = int(index[:-1])  # strip the closing bracket
                    child.value = default_simulation_config[base_key][index]
                else:
                    child.value = default_simulation_config[child.key]

    # Reset sim with the fresh config
    reset_simulation()

# Window
window.size = (1280, 720)
window.borderless = False

# DEBUGGING - GIVES AN AVERAGE SPEED READOUT AND SPECIFIC SPEEDS FOR FIRST 3 AGENTS
#speed_readout = Text(text="Avg Speed: 0.0", position=(-0.7, 0.4), scale=2, color=color.white)
#first_agent_speed_readout = Text(text="First Agent Speed: 0.0", position=(-0.7, 0.3), scale=2, color=color.white)
#second_agent_speed_readout = Text(text="Second Agent Speed: 0.0", position=(-0.7, 0.2), scale=2, color=color.white)
#third_agent_speed_readout = Text(text="Third Agent Speed: 0.0", position=(-0.7, 0.1), scale=2, color=color.white)

# Create the settings UI and get the containers.
ui_elements = create_settings_ui()
background_dimmer = ui_elements['background_dimmer']
physics_ui = ui_elements['physics_ui']
simulation_ui = ui_elements['simulation_ui']
agents_ui = ui_elements['agents_ui']
movement_ui = ui_elements['movement_ui']
settings_containers = ui_elements['settings_containers']
camera_ui = ui_elements['camera_ui']

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

movement_button = Button(text="Movement", parent=camera.ui,
                      position=(-0.7, 0.1), scale=(0.2, 0.05))
movement_button.on_click = lambda: toggle_settings(movement_ui, background_dimmer, settings_containers)

camera_button = Button(text="Camera", parent=camera.ui,
                       position=(-0.7, -0.0), scale=(0.2, 0.05))
camera_button.on_click = lambda: toggle_settings(camera_ui, background_dimmer, settings_containers)

reset_button = Button(text="Reset Sim", parent=camera.ui,
                      position=(-0.7, -0.1, -0.5), scale=(0.2, 0.05), color=color.azure)
reset_button.on_click = reset_simulation

reset_default_button = Button(text="Reset Default", parent=camera.ui,
                              position=(-0.7, -0.2, -0.5), scale=(0.2, 0.05), color=color.orange)
reset_default_button.on_click = reset_simulation_to_default

orbit_toggle = Button(text="Auto Orbit: Off", parent=camera_ui,
                      position=(-0.15, -0.00), scale=(0.4, 0.05), color=color.blue)
orbit_toggle.on_click = lambda: (
    toggle_auto_rotate(),
    setattr(orbit_toggle, 'text', f"Auto Orbit: {'On' if auto_rotate_enabled else 'Off'}")
)

reset_bounds_button = Button(
    text="Reset Boundaries", parent=simulation_ui,
    position=(-0.15, -0.10), scale=(0.4, 0.05), color=color.blue
)
reset_bounds_button.on_click = reset_boundaries



# Run the Ursina app
app.run()