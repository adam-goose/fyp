
simulation_config = {
    # Core Physics Variables
    "perception_radius": 3.0,
    "collision_radius": 0,
    "min_speed": 0.0,
    "max_speed": 5.0,
    "desired_speed": 2.0,
    "acceleration": 0.01,
    "deceleration": 0.05,
    "momentum_weight": 10.0,
    "delta_time": 0.1,
    "heading_alignment_threshold": 0.9,

    # Cohesion, Alignment, Separation
    "cohesion_radius": 3.0,
    "cohesion_weight": 1.0,
    "alignment_radius": 2.0,
    "alignment_weight": 1.5,
    "separation_radius": 1.0,
    "separation_weight": 2.0,

    # Simulation Variables
    "camera_position": (25, 20, -70),       # Camera position
    "camera_look_at": (0, 0, 0),            # Where the camera looks
    "frame_duration": 1/60,                 # Duration of the frame per second
    "num_agents": 30,                       # Number of agents
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
    "wall_repulsion_weight": 0.01,
    "boundary_threshold": 2.0,
    "boundary_max_force": 10.0
}