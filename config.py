from copy import deepcopy

def get_movement_model_by_name(name):
    if name == "Boids":
        from movement_model import Boids
        return Boids()
    # Add other models here
    raise ValueError(f"Unknown movement model: {name}")

def update_config(key, slider):
    val = slider.value

    if '[' in key and ']' in key:
        base_key, index = key.split('[')
        index = int(index.rstrip(']'))
        simulation_config[base_key][index] = val
    else:
        simulation_config[key] = val

    if key == "num_agents":
        val = int(round(val))  # clean integer, no floaty nonsense

    # Symmetric boundary logic
    if key == "x_max":
        simulation_config["x_min"] = -val
    elif key == "y_max":
        simulation_config["y_min"] = -val
    elif key == "z_max":
        simulation_config["z_min"] = -val

    simulation_config[key] = val


simulation_config = {
    # Core Physics Variables
    "perception_radius": 3.0,
    "min_speed": 0.1, # Hidden
    "max_speed": 2.0,
    "acceleration": 0.001,
    "deceleration": 0.001,
    "momentum_weight": 1.0,
    "direction_alpha": 0.1, # Hidden
    "turn_sensitivity": 5,

    # Cohesion, Alignment, Separation
    "cohesion_radius": 3.0,
    "cohesion_weight": 1.0,
    "alignment_radius": 2.0,
    "alignment_weight": 1.5,
    "separation_radius": 1.0,
    "separation_weight": 2.0,

    # Simulation Variables
    "movement_model": "Boids",              # The movement model
    "camera_position": [25, 20, -75],       # Camera position
    "camera_look_at": [0, 0, 0],            # Where the camera looks
    "camera_orbit_speed": 1,
    "frame_duration": 1/60,                 # Duration of the frame per second # TO BE INVESTIGATED - Higher rate seems to make smoother movement?
    "num_agents": 4,                       # Number of agents
    "init_position_bounds": (-10, 10),      # Initial spawned position range for agents
    "init_direction_bounds": (-1.0, 1.0),   # Initial spawned direction range for agents
    "init_speed_bounds": (0.01, 0.1),       # Initial spawned speed range for agents
    "agent_scale": 0.2,                     # Scale of the agent entity in Ursina
    "agent_colour_mode": "multi",

    # Simulation Boundaries
    "x_max": 10,
    "x_min": -10,
    "y_max": 10,
    "y_min": -10,
    "z_max": 10,
    "z_min": -10,
    "wall_repulsion_weight": 1.0,
    "boundary_threshold": 2.0,
    "boundary_max_force": 10.0
}

default_simulation_config = deepcopy(simulation_config)