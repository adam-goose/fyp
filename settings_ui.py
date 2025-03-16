# settings_ui.py
from ursina import *
from config import update_config
from config import *

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
    {"min": 0, "max": 12, "default": simulation_config["num_agents"], "text": "Number of Agents", "key": "num_agents"},
    {"min": 0, "max": 1, "default": simulation_config["agent_scale"], "text": "Agent Size", "key": "agent_scale"},
    {"min": 0, "max": 12, "default": simulation_config["x_max"], "text": "X Boundary", "key": "x_max"},
    {"min": 0, "max": 12, "default": simulation_config["y_max"], "text": "Y Boundary", "key": "y_max"},
    {"min": 0, "max": 12, "default": simulation_config["z_max"], "text": "Z Boundary", "key": "z_max"},
]

physics_sliders = [
    {"min": 0.00, "max": 10, "default": simulation_config["wall_repulsion_weight"], "text": "Boundary Repulsion Multiplier", "key": "wall_repulsion_weight"},
    {"min": 0.01, "max": 12, "default": simulation_config["boundary_threshold"], "text": "Boundary Threshold", "key": "boundary_threshold"},
    {"min": 0.00, "max": 10, "default": simulation_config["boundary_max_force"], "text": "Boundary Force", "key": "boundary_max_force"},
]


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

    # List of all settings containers for easy toggling.
    settings_containers = [physics_ui, simulation_ui, agents_ui, movement_ui]

    # Create the UI elements for each category.
    create_sliders(physics_ui, physics_sliders)
    create_sliders(simulation_ui, simulation_sliders)
    create_sliders(agents_ui, agent_sliders)
    create_sliders(movement_ui, movement_sliders)

    # Return the containers and background dimmer for external access.
    return {
        'background_dimmer': background_dimmer,
        'physics_ui': physics_ui,
        'simulation_ui': simulation_ui,
        'agents_ui': agents_ui,
        'movement_ui': movement_ui,
        'settings_containers': settings_containers
    }

def create_sliders(container, slider_data):
    """Helper function to create sliders for a given container."""
    for i, data in enumerate(slider_data):
        slider = Slider(
            min=data['min'],
            max=data['max'],
            default=data['default'],
            parent=container,
            position=(-0.2, 0.4 - i * 0.1),
            scale=(1, 1),
            text=data['text']
        )
        slider.children[0].z = -1  # Lowering the z value draws it on top.
        if 'key' in data:
            slider.on_value_changed = lambda s=slider, k=data['key']: update_config(k, s)

def update_background_dimmer(background_dimmer, settings_containers):
    """Update the background dimmer based on whether any settings container is active."""
    background_dimmer.enabled = any(container.enabled for container in settings_containers)

def toggle_settings(container, background_dimmer, settings_containers):
    """Toggle a specific settings container and disable all others."""
    for c in settings_containers:
        c.enabled = c == container and not c.enabled
    update_background_dimmer(background_dimmer, settings_containers)