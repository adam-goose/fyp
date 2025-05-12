from copy import deepcopy
from ursina import color, Entity
import numpy as np

def get_movement_model_by_name(name):
    """
    Factory function to return a movement model instance based on its string name.
    Currently only supports 'Boids'.

    :param name: Name of the movement model.
    :return: Instance of the selected movement model class.
    """
    if name == "Boids":
        from movement_model import Boids
        return Boids()
    raise ValueError(f"Unknown movement model: {name}")

def update_config(key, slider):
    """
    Update the simulation configuration dictionary using a slider's value.
    Handles both single-value keys and indexed values (e.g., camera_position[0]).
    Applies symmetry to min/max boundaries when needed.

    :param key: Configuration key string, may include indexing.
    :param slider: Ursina Slider object with a `.value` field.
    """
    val = slider.value

    if '[' in key and ']' in key:
        base_key, index = key.split('[')
        index = int(index.rstrip(']'))
        simulation_config[base_key][index] = val
    else:
        simulation_config[key] = val

    # Round to integer if needed
    if key == "num_agents":
        val = int(round(val))

    # Maintain symmetry for simulation bounds
    if key == "x_max":
        simulation_config["x_min"] = -val
    elif key == "y_max":
        simulation_config["y_min"] = -val
    elif key == "z_max":
        simulation_config["z_min"] = -val

    simulation_config[key] = val

def pack_boundaries(config):
    """
    Pack boundary values from config into a 1D NumPy array.

    :param config: The simulation configuration dictionary.
    :return: Array [x_min, x_max, y_min, y_max, z_min, z_max].
    """
    return np.array([
        config["x_min"],
        config["x_max"],
        config["y_min"],
        config["y_max"],
        config["z_min"],
        config["z_max"]
    ], dtype=np.float32)

def unpack_boundaries(boundary_array, config):
    """
    Unpack boundary array values into the config dictionary.

    :param boundary_array: Array [x_min, x_max, y_min, y_max, z_min, z_max].
    :param config: The simulation configuration dictionary to update.
    """
    config["x_min"] = boundary_array[0]
    config["x_max"] = boundary_array[1]
    config["y_min"] = boundary_array[2]
    config["y_max"] = boundary_array[3]
    config["z_min"] = boundary_array[4]
    config["z_max"] = boundary_array[5]

# Main configuration dictionary for simulation
simulation_config = {
    # --- Physics and Behavior ---
    "perception_radius": 3.0,
    "min_speed": 0.1,                # Hidden (used internally)
    "max_speed": 2.0,
    "acceleration": 0.001,
    "deceleration": 0.001,
    "momentum_weight": 1.0,
    "direction_alpha": 0.1,         # Hidden (controls inertia)
    "turn_sensitivity": 5,

    # --- Flocking Parameters ---
    "cohesion_radius": 3.0,
    "cohesion_weight": 1.0,
    "alignment_radius": 2.0,
    "alignment_weight": 1.5,
    "separation_radius": 1.0,
    "separation_weight": 2.0,

    # --- Simulation Control ---
    "movement_model": "Boids",
    "camera_position": [25, 20, -75],
    "camera_look_at": [0, 0, 0],
    "camera_orbit_speed": 1,
    "frame_duration": 1/60,
    "num_agents": 10,
    "init_direction_bounds": (-1.0, 1.0),
    "init_speed_bounds": (0.01, 0.1),
    "agent_scale": 2,
    "agent_colour_mode": "white",
    "fish_texture_enabled": True,

    # --- World Boundaries ---
    "x_max": 10,
    "x_min": -10,
    "y_max": 10,
    "y_min": -10,
    "z_max": 10,
    "z_min": -10,
    "wall_repulsion_weight": 1.0,
    "boundary_threshold": 2.0,
    "boundary_max_force": 10.0,

    # --- Obstacle Parameters ---
    "obstacle_enabled": False,
    "obstacle_corner_min": [-10, 0, -10],
    "obstacle_corner_max": [10, 1, 10],
    "obstacle_colour": color.white,
}

# A clean copy used for resets or reloads
default_simulation_config = deepcopy(simulation_config)
