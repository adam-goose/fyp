
simulation_config = {
    # Core Physics Variables
    "perception_radius": 3.0,
    "collision_radius": 0,
    "min_speed": 0.0,
    "max_speed": 2.0,
    "desired_speed": 2.0,
    "acceleration": 0,
    "momentum_weight": 1.0,
    "delta_time": 0.1,

    # Cohesion, Alignment, Separation
    "cohesion_radius": 3.0,
    "cohesion_weight": 1.0,
    "alignment_radius": 2.0,
    "alignment_weight": 1.5,
    "separation_radius": 1.0,
    "separation_weight": 2.0,

    # Simulation Variables
    "num_agents": 25,                   # Number of agents
    "position_bounds": (-10, 10),       # Position range for x, y, z
    "direction_bounds": (-1.0, 1.0),    # Direction range for x, y, z
    "speed_bounds": (0.1, 0.2),         # Speed range

    # Simulation Boundaries
    "x_max": 10,
    "x_min": -10,
    "y_max": 10,
    "y_min": -10,
    "z_max": 10,
    "z_min": -10,
    "wall_repulsion_weight": 1.0,
}