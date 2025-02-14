def get_movement_model_by_name(name):
    if name == "Boids":
        from movement_model import Boids
        return Boids()
    # Add other models here
    raise ValueError(f"Unknown movement model: {name}")

def update_config(key, slider):
    simulation_config[key] = slider.value
    print(f"{key} updated to: {simulation_config[key]}")

simulation_config = {
    # Core Physics Variables
    "perception_radius": 3.0,
    "min_speed": 0.1,
    "max_speed": 2.0,
    "desired_speed": 2.0,
    "acceleration": 0.01,
    "deceleration": 5000,
    "max_lateral_acceleration": 0.1,
    "momentum_weight": 10.0,
    "dt": 0.1,
    "turning_threshold": 0.9,
    "heading_alignment_threshold": 0.1,

    # Cohesion, Alignment, Separation
    "cohesion_radius": 3.0,
    "cohesion_weight": 1.0,
    "alignment_radius": 2.0,
    "alignment_weight": 1.5,
    "separation_radius": 1.0,
    "separation_weight": 2.0,

    # Simulation Variables
    "movement_model": "Boids",              # The movement model
    "camera_position": (25, 20, -70),       # Camera position
    "camera_look_at": (0, 0, 0),            # Where the camera looks
    "frame_duration": 1/60,                 # Duration of the frame per second
    "num_agents": 50,                       # Number of agents
    "init_position_bounds": (-10, 10),      # Initial spawned position range for agents
    "init_direction_bounds": (-1.0, 1.0),   # Initial spawned direction range for agents
    "init_speed_bounds": (0.01, 0.1),       # Initial spawned speed range for agents
    "agent_scale": 0.2,                     # Scale of the agent entity in Ursina

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