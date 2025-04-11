# settings_ui.py
from ursina import *
from config import update_config
from config import *
from simulation import refresh_obstacle

# Define Slider data for each category with updated menus: Agent, Simulation, and Physics.
movement_sliders = [
    {"min": 0, "max": 10, "default": simulation_config["perception_radius"], "text": "Perception Radius","key": "perception_radius"},
    {"min": 0, "max": 10, "default": simulation_config["cohesion_radius"], "text": "Cohesion Radius", "key": "cohesion_radius"},
    {"min": 0, "max": 10, "default": simulation_config["cohesion_weight"], "text": "Cohesion Weight", "key": "cohesion_weight"},
    {"min": 0, "max": 10, "default": simulation_config["separation_radius"], "text": "Separation Radius", "key": "separation_radius"},
    {"min": 0, "max": 10, "default": simulation_config["separation_weight"], "text": "Separation Weight", "key": "separation_weight"},
    {"min": 0, "max": 10, "default": simulation_config["alignment_radius"], "text": "Alignment Radius", "key": "alignment_radius"},
    {"min": 0, "max": 10, "default": simulation_config["alignment_weight"], "text": "Alignment Weight", "key": "alignment_weight"},
]

agent_sliders = [
    {"min": 0, "max": 12, "default": simulation_config["max_speed"], "text": "Max Speed", "key": "max_speed"},
    {"min": 0, "max": 0.01, "default": simulation_config["acceleration"], "text": "Acceleration", "key": "acceleration"},
    {"min": 0, "max": 0.01, "default": simulation_config["deceleration"], "text": "Deceleration", "key": "deceleration"},
    {"min": 0.01, "max": 4, "default": simulation_config["momentum_weight"], "text": "Momentum", "key": "momentum_weight"},
    {"min": 0, "max": 10, "default": simulation_config["turn_sensitivity"], "text": "Turn Sensitivity", "key": "turn_sensitivity"},
]

simulation_sliders = [
    {"min": 0, "max": 100, "default": simulation_config["num_agents"], "text": "Number of Agents", "key": "num_agents"},
    {"min": 0.1, "max": 2, "default": simulation_config["agent_scale"], "text": "Agent Size", "key": "agent_scale"},
    {"min": 0, "max": 15, "default": simulation_config["x_max"], "text": "X Boundary", "key": "x_max"},
    {"min": 0, "max": 15, "default": simulation_config["y_max"], "text": "Y Boundary", "key": "y_max"},
    {"min": 0, "max": 15, "default": simulation_config["z_max"], "text": "Z Boundary", "key": "z_max"},
]

physics_sliders = [
    {"min": 0.01, "max": 12, "default": simulation_config["boundary_threshold"], "text": "Boundary Threshold", "key": "boundary_threshold"},
    {"min": 0.00, "max": 100, "default": simulation_config["wall_repulsion_weight"], "text": "Repulsion Multiplier", "key": "wall_repulsion_weight"},
    {"min": 0.00, "max": 10, "default": simulation_config["boundary_max_force"], "text": "Boundary Force", "key": "boundary_max_force"},
]

camera_sliders = [
    {"min": -100, "max": 100, "default": simulation_config["camera_position"][0], "text": "Camera X", "key": "camera_position[0]"},
    {"min": -100, "max": 100, "default": simulation_config["camera_position"][1], "text": "Camera Y", "key": "camera_position[1]"},
    {"min": -100, "max": 100, "default": simulation_config["camera_position"][2], "text": "Camera Z", "key": "camera_position[2]"},
    {"min": 0, "max": 2, "default": simulation_config["camera_orbit_speed"], "text": "Orbit Speed", "key": "camera_orbit_speed"},
]

obstacle_sliders = [
    {"min": -15, "max": 15, "step": 0.1, "default": simulation_config["obstacle_corner_min"][0], "text": "Obstacle Min X", "key": "obstacle_corner_min[0]"},
    {"min": -15, "max": 15, "step": 0.1, "default": simulation_config["obstacle_corner_min"][1], "text": "Obstacle Min Y", "key": "obstacle_corner_min[1]"},
    {"min": -15, "max": 15, "step": 0.1, "default": simulation_config["obstacle_corner_min"][2], "text": "Obstacle Min Z", "key": "obstacle_corner_min[2]"},
    {"min": -15, "max": 15, "step": 0.1, "default": simulation_config["obstacle_corner_max"][0], "text": "Obstacle Max X", "key": "obstacle_corner_max[0]"},
    {"min": -15, "max": 15, "step": 0.1, "default": simulation_config["obstacle_corner_max"][1], "text": "Obstacle Max Y", "key": "obstacle_corner_max[1]"},
    {"min": -15, "max": 15, "step": 0.1, "default": simulation_config["obstacle_corner_max"][2], "text": "Obstacle Max Z", "key": "obstacle_corner_max[2]"},
]

def update_agent_color(color_name):
    simulation_config['agent_colour_mode'] = color_name
    print(f"Agent colour set to: {color_name}")

def update_obstacle_color(color):
    simulation_config['obstacle_colour'] = color
    refresh_obstacle()
    print(f"Obstacle colour set to: {color}")

def toggle_obstacle():
    simulation_config['obstacle_enabled'] = not simulation_config['obstacle_enabled']
    refresh_obstacle()
    print(f"Obstacle enabled: {simulation_config['obstacle_enabled']}")

def create_settings_ui():
    """Create all settings UI elements and return the containers."""
    # Create a full-screen background dimmer.
    background_dimmer = Entity(
        parent=camera.ui,
        model='quad',
        scale=(2, 2),  # This should cover the entire screen.
        color=color.rgba(0, 0, 0, 0.4),  # A semi-transparent black.
        enabled=False
    )

    # Create containers for each settings category.
    physics_ui = Entity(parent=camera.ui, enabled=False)
    simulation_ui = Entity(parent=camera.ui, enabled=False)
    agents_ui = Entity(parent=camera.ui, enabled=False)
    movement_ui = Entity(parent=camera.ui, enabled=False)
    camera_ui = Entity(parent=camera.ui, enabled=False)
    obstacle_ui = Entity(parent=camera.ui, enabled=False)

    # List of all settings containers for easy toggling.
    settings_containers = [physics_ui, simulation_ui, agents_ui, movement_ui, camera_ui, obstacle_ui]

    # Create the UI elements for each category.
    create_sliders(physics_ui, physics_sliders)
    create_sliders(simulation_ui, simulation_sliders)
    create_sliders(agents_ui, agent_sliders)
    colors = ['multi', 'red', 'blue', 'green', 'yellow', 'white', 'black']
    for i, color_name in enumerate(colors):
        Button(
            text=color_name,
            color=getattr(color, color_name, color.gray) if color_name != 'multi' else color.white66,
            scale=(0.1, 0.05),
            position=(i * 0.12 - 0.35, -0.10),  # centered layout
            parent=agents_ui,
            on_click=lambda c=color_name: update_agent_color(c)
        )

    create_sliders(movement_ui, movement_sliders)
    create_sliders(camera_ui, camera_sliders)
    create_sliders(obstacle_ui, obstacle_sliders)
    for i, color_name in enumerate(colors[1:]):
        Button(
            text=color_name,
            color=getattr(color, color_name, color.gray),
            scale=(0.1, 0.05),
            position=(i * 0.12 - 0.35, -0.20),  # centered layout
            parent=obstacle_ui,
            on_click=lambda c=getattr(color, color_name): update_obstacle_color(c)
        )
        obstacle_toggle = Button(
            text="Toggle Obstacle",
            color=color.blue,
            parent=obstacle_ui,
            position=(-0.2, -0.3),
            scale=(0.4, 0.05))
        obstacle_toggle.on_click = lambda: toggle_obstacle()


    # Return the containers and background dimmer for external access.
    return {
        'background_dimmer': background_dimmer,
        'physics_ui': physics_ui,
        'simulation_ui': simulation_ui,
        'agents_ui': agents_ui,
        'movement_ui': movement_ui,
        'settings_containers': settings_containers,
        'camera_ui': camera_ui,
        'obstacle_ui': obstacle_ui
    }

def create_sliders(container, slider_data):
    """Helper function to create sliders for a given container."""
    for i, data in enumerate(slider_data):
        slider = Slider(
            key = data['key'],  # 👈 Attach the key directly to the slider
            min=data['min'],
            max=data['max'],
            default=data['default'],
            parent=container,
            position=(-0.2, 0.4 - i * 0.1),
            scale=(1, 1),
            text=data['text']
        )
        if data['key'] in ['camera_position[0]', 'camera_position[1]', 'camera_position[2]']:
            if len(slider.children) > 2:
                slider.children[2].text = ""  # ← Erases the text content, leaves slider button intact

        slider.children[0].z = -1  # Lowering the z value draws it on top.

        key = data['key']

        if key in ['camera_position[0]', 'camera_position[1]', 'camera_position[2]']:
            slider.update = lambda s=slider, k=key: update_config(k, s)

        if 'key' in data:
            if data['key'] == "num_agents":
                def snap_to_int(sl=slider, k=data['key']):
                    sl.value = round(sl.value)  # snap visually
                    update_config(k, sl)  # pass the slider object as expected

                slider.on_value_changed = snap_to_int

            else:
                slider.on_value_changed = lambda s=slider, k=data['key']: (
                    update_config(k, s),
                    refresh_obstacle()
                )

def update_background_dimmer(background_dimmer, settings_containers):
    """Update the background dimmer based on whether any settings container is active."""
    background_dimmer.enabled = any(container.enabled for container in settings_containers)

def toggle_settings(container, background_dimmer, settings_containers):
    """Toggle a specific settings container and disable all others."""
    for c in settings_containers:
        c.enabled = c == container and not c.enabled
    update_background_dimmer(background_dimmer, settings_containers)