# settings_ui.py
from ursina import *
from config import update_config

# Define Slider data for each category with updated menus: Agent, Simulation, and Physics.

agent_sliders = [
    {"min": 0, "max": 12, "default": 5.0, "text": "Max Speed", "key": "max_speed"},
    {"min": 0, "max": 12, "default": 2.0, "text": "Desired Speed", "key": "desired_speed"},
    {"min": 0, "max": 1, "default": 0.01, "text": "Acceleration", "key": "acceleration"},
    {"min": 0, "max": 100, "default": 0.05, "text": "Deceleration", "key": "deceleration"},
    {"min": 0, "max": 0.2, "default": 0.1, "text": "Max Lateral Acc", "key": "max_lateral_acceleration"},
    {"min": 0, "max": 100, "default": 10.0, "text": "Momentum", "key": "momentum_weight"},
    {"min": 0, "max": 1, "default": 0.9, "text": "Turning Threshold", "key": "turning_threshold"},
    {"min": 0, "max": 12, "default": 0.2, "text": "Scale", "key": "agent_scale"},
]

simulation_sliders = [
    {"min": 0, "max": 12, "default": 0.1, "text": "Delta Time", "key": "dt"},
    {"min": 0, "max": 12, "default": 50, "text": "Number of Agents", "key": "num_agents"},
    {"min": 1/60, "max": 60/60, "default": 1/60, "text": "Frame Duration", "key": "frame_duration"},
    {"min": 0, "max": 12, "default": 10, "text": "X Boundary", "key": "x_max"},
    {"min": 0, "max": 12, "default": 10, "text": "Y Boundary", "key": "y_max"},
    {"min": 0, "max": 12, "default": 10, "text": "Z Boundary", "key": "z_max"},

]

physics_sliders = [
    {"min": 0, "max": 12, "default": 1.0, "text": "Wall Repulsion", "key": "wall_repulsion_weight"},
    {"min": 0, "max": 12, "default": 2.0, "text": "Boundary Threshold", "key": "boundary_threshold"},
    {"min": 0, "max": 12, "default": 10.0, "text": "Boundary Force", "key": "boundary_max_force"},
    {"min": 0, "max": 12, "default": 0.0, "text": "Gravity", "key": "gravity"},  # Assuming gravity isn't explicitly set
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

    # List of all settings containers for easy toggling.
    settings_containers = [physics_ui, simulation_ui, agents_ui]

    # Create the UI elements for each category.
    create_sliders(physics_ui, physics_sliders)
    create_sliders(simulation_ui, simulation_sliders)
    create_sliders(agents_ui, agent_sliders)

    # Return the containers and background dimmer for external access.
    return {
        'background_dimmer': background_dimmer,
        'physics_ui': physics_ui,
        'simulation_ui': simulation_ui,
        'agents_ui': agents_ui,
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