import numpy as np
from config import simulation_config

# Core Agent Variables
position = np.array([pos1, pos2, pos3])
direction = np.array([dir1, dir2, dir3])
speed = 0

# Behaviour Variables
perception_range =  simulation_config["perception_range"]
avoidance_radius =  simulation_config["avoidance_radius"]
max_speed =         simulation_config["max_speed"]
acceleration =      simulation_config["acceleration"]