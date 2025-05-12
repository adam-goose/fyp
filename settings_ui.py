from ursina import *
from config import update_config, simulation_config, default_simulation_config
from simulation import refresh_obstacle, reset_boundaries, redraw_agents, reset_simulation


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
    {"min": 1, "max": 3, "default": simulation_config["agent_scale"], "text": "Agent Size", "key": "agent_scale"},
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

_redraw_callback = None

def register_redraw_callback(cb):
    """
    Register a callback function to be triggered after redraw-worthy changes.

    :param cb: A function that triggers a visual update.
    """
    global _redraw_callback
    _redraw_callback = cb

# --- BUTTON PANEL SETUP ---
def build_button_panel(settings_containers, background_dimmer, ui_refs):
    """
    Build and return the main left panel of category toggle buttons.

    :param settings_containers: All settings UI panels.
    :param background_dimmer: UI dimmer entity.
    :param ui_refs: Dictionary containing named panels.
    """
    button_specs = [
        ("Physics", ui_refs['physics_ui'], 0.4),
        ("Simulation", ui_refs['simulation_ui'], 0.32),
        ("Agent", ui_refs['agents_ui'], 0.24),
        ("Movement", ui_refs['movement_ui'], 0.16),
        ("Camera", ui_refs['camera_ui'], 0.08),
        ("Obstacle", ui_refs['obstacle_ui'], 0.0),
    ]

    for name, panel, y in button_specs:
        Button(
            text=name,
            parent=camera.ui,
            position=(-0.7, y),
            scale=(0.2, 0.05),
            on_click=lambda c=panel: toggle_settings(c, background_dimmer, settings_containers)
        )


# --- CONTROL BUTTONS ---
def build_control_buttons(reset_fn, reset_default_fn, toggle_recording_fn, toggle_playback_fn):
    """
    Build and return action buttons for reset, playback, and recording.
    Bound to their respective functions passed from main.
    """
    global record_toggle, playback_toggle

    Button(
        text="Reset Sim",
        parent=camera.ui,
        position=(-0.7, -0.08, -0.5),
        scale=(0.2, 0.05),
        color=color.azure,
        on_click=reset_fn
    )

    Button(
        text="Reset Default",
        parent=camera.ui,
        position=(-0.7, -0.16, -0.5),
        scale=(0.2, 0.05),
        color=color.orange,
        on_click=reset_default_fn
    )

    record_toggle = Button(
        text='Start Recording',
        parent=camera.ui,
        position=(-0.7, -0.24, -0.5),
        scale=(0.2, 0.05),
        color=color.red,
        on_click=toggle_recording_fn
    )

    playback_toggle = Button(
        text='Play Recording',
        parent=camera.ui,
        position=(-0.7, -0.32, -0.5),
        scale=(0.2, 0.05),
        color=color.green,
        on_click=toggle_playback_fn
    )

    return record_toggle, playback_toggle


# --- CAMERA TOGGLE ---
def build_orbit_toggle(camera_panel, toggle_fn):
    """
    Toggle for automatic camera orbiting.

    :param camera_panel: UI panel for camera settings.
    :param toggle_fn: Function to enable/disable orbiting.
    """
    def handle_toggle():
        toggle_fn()
        orbit_toggle.text = f"Auto Orbit: {'On' if simulation_config.get('auto_rotate', False) else 'Off'}"

    orbit_toggle = Button(
        text="Auto Orbit: Off",
        parent=camera_panel,
        position=(-0.15, -0.00),
        scale=(0.4, 0.05),
        color=color.blue,
        on_click=handle_toggle
    )

# --- CONFIG UPDATE HANDLERS ---
def update_agent_color(color_name):
    """
    Change the agent color mode in config and trigger redraw.

    :param color_name: The selected color name (e.g., 'red', 'multi').
    """
    simulation_config['agent_colour_mode'] = color_name
    print(f"Agent colour set to: {color_name}")
    if _redraw_callback:
        _redraw_callback()

def update_obstacle_color(color):
    """
    Update the color used for the obstacle in the simulation.

    :param color: Ursina color object.
    """
    simulation_config['obstacle_colour'] = color
    refresh_obstacle()
    print(f"Obstacle colour set to: {color}")

def toggle_obstacle():
    """
    Toggle the visibility and presence of the obstacle in the scene.
    """
    simulation_config['obstacle_enabled'] = not simulation_config['obstacle_enabled']
    refresh_obstacle()
    print(f"Obstacle enabled: {simulation_config['obstacle_enabled']}")

def toggle_fish_texture():
    """
    Toggle whether agents use their texture or plain color.
    """
    simulation_config['fish_texture_enabled'] = not simulation_config.get('fish_texture_enabled', True)
    print(f"Fish texture enabled: {simulation_config['fish_texture_enabled']}")
    if _redraw_callback:
        _redraw_callback()

# --- SLIDER GENERATION ---
def create_sliders(container, slider_data):
    """
    Generate sliders dynamically based on a list of slider configuration dicts.

    :param container: UI entity to parent sliders to.
    :param slider_data: List of dictionaries defining slider params.
    """
    boundary_keys = ['x_max', 'y_max', 'z_max']

    for i, data in enumerate(slider_data):
        # Create the slider
        slider = Slider(
            key = data['key'],
            min=data['min'],
            max=data['max'],
            default=data['default'],
            parent=container,
            position=(-0.2, 0.4 - i * 0.1),
            scale=(1, 1),
            text=data['text']
        )

        # Remove label text for camera sliders
        if data['key'] in ['camera_position[0]', 'camera_position[1]', 'camera_position[2]']:
            if len(slider.children) > 2:
                slider.children[2].text = ""

        # Move numeric value below the slider
        slider.children[0].z = -1
        key = data['key']

        # Bind camera sliders to config update on slider drag
        if key in ['camera_position[0]', 'camera_position[1]', 'camera_position[2]']:
            slider.update = lambda s=slider, k=key: update_config(k, s)

        # Bind special snapping for integer-only sliders (e.g. number of agents)
        if key == "num_agents":
            def snap_to_int(sl=slider, k=key):
                sl.value = round(sl.value)
                update_config(k, sl)
            slider.on_value_changed = snap_to_int
        else:
            # General config update binding
            def on_value_changed(s=slider, k=key):
                update_config(k, s)
                refresh_obstacle()
                if k in boundary_keys:
                    reset_boundaries()
            slider.on_value_changed = on_value_changed

# --- UI ELEMENTS ---
def build_color_buttons(parent):
    """
    Add a row of color buttons to the given parent UI element.

    :param parent: UI container.
    """
    color_options = ['multi', 'red', 'blue', 'green', 'yellow', 'white', 'black']
    for i, color_name in enumerate(color_options):
        # Each button sets the corresponding agent color mode
        Button(
            text=color_name,
            color=getattr(color, color_name, color.gray) if color_name != 'multi' else color.white66,
            scale=(0.1, 0.05),
            position=(i * 0.12 - 0.35, -0.10),
            parent=parent,
            on_click=lambda c=color_name: update_agent_color(c)
        )

def build_texture_toggle(parent):
    """
    Add a toggle button to switch fish texture on/off.

    :param parent: UI container.
    """
    return Button(
        text="Toggle Fish Texture",
        color=color.blue,
        parent=parent,
        position=(-0.2, -0.2),
        scale=(0.4, 0.05),
        on_click=toggle_fish_texture
    )

def build_obstacle_controls(parent):
    """
    Add color buttons and toggle control for obstacle UI.

    :param parent: UI container.
    """
    color_options = ['red', 'blue', 'green', 'yellow', 'white', 'black']
    for i, color_name in enumerate(color_options):
        # Each button updates the obstacle color to a preset value
        Button(
            text=color_name,
            color=getattr(color, color_name, color.gray),
            scale=(0.1, 0.05),
            position=(i * 0.12 - 0.35, -0.20),
            parent=parent,
            on_click=lambda c=getattr(color, color_name): update_obstacle_color(c)
        )

    # A toggle to enable or disable the obstacle object in the scene
    return Button(
        text="Toggle Obstacle",
        color=color.blue,
        parent=parent,
        position=(-0.2, -0.3),
        scale=(0.4, 0.05),
        on_click=toggle_obstacle
    )

# --- MAIN UI CREATION ---
def create_settings_ui(on_reset_click=None, on_record_click=None, on_playback_click=None):
    """
    Construct and return all main UI containers and widgets for settings categories.

    :return: Dictionary mapping of key UI sections and container references.
    """
    # Background overlay when any settings panel is active
    background_dimmer = Entity(
        parent=camera.ui,
        model='quad',
        scale=(2, 2),
        color=color.rgba(0, 0, 0, 0.4),
        enabled=False
    )

    # Create container panels for each category of settings
    physics_ui = Entity(parent=camera.ui, enabled=False)
    simulation_ui = Entity(parent=camera.ui, enabled=False)
    agents_ui = Entity(parent=camera.ui, enabled=False)
    movement_ui = Entity(parent=camera.ui, enabled=False)
    camera_ui = Entity(parent=camera.ui, enabled=False)
    obstacle_ui = Entity(parent=camera.ui, enabled=False)

    # Group all the UI tabs for toggling visibility and background dimming
    settings_containers = [physics_ui, simulation_ui, agents_ui, movement_ui, camera_ui, obstacle_ui]

    # Populate each panel with its associated sliders and controls
    create_sliders(physics_ui, physics_sliders)
    create_sliders(simulation_ui, simulation_sliders)
    create_sliders(agents_ui, agent_sliders)
    build_color_buttons(agents_ui)
    build_texture_toggle(agents_ui)
    create_sliders(movement_ui, movement_sliders)
    create_sliders(camera_ui, camera_sliders)
    create_sliders(obstacle_ui, obstacle_sliders)
    build_obstacle_controls(obstacle_ui)

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

def update_background_dimmer(background_dimmer, settings_containers):
    """
    Enable or disable background overlay depending on any active settings tab.

    :param background_dimmer: UI overlay entity.
    :param settings_containers: List of category panels.
    """
    background_dimmer.enabled = any(container.enabled for container in settings_containers)

def toggle_settings(container, background_dimmer, settings_containers):
    """
    Toggle visibility for the selected settings panel, hiding all others.

    :param container: Panel to toggle.
    :param background_dimmer: Overlay entity.
    :param settings_containers: All UI tabs.
    """
    for c in settings_containers:
        c.enabled = c == container and not c.enabled
    update_background_dimmer(background_dimmer, settings_containers)

def reset_simulation_to_default(settings_containers):
    """
    Reset all config values and sliders to their default state.
    Then resets the simulation using core logic.
    """
    for key, value in default_simulation_config.items():
        simulation_config[key] = value

    for container in settings_containers:
        for child in container.children:
            if isinstance(child, Slider) and hasattr(child, 'key'):
                if '[' in child.key and ']' in child.key:
                    base_key, index = child.key.split('[')
                    index = int(index[:-1])
                    child.value = default_simulation_config[base_key][index]
                else:
                    child.value = default_simulation_config[child.key]

    reset_simulation()
