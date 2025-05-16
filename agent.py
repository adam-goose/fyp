"""
Author: Adam Zelenak
Part of the 3D Swarm Simulation Project
File: agent.py
Description: Defines individual agent state, including position, velocity, and update logic.
"""

import random
import numpy as np
from config import *

class Agent:
    """
    Represents an individual agent in the swarm simulation.

    Each agent has position, direction, and speed, and contributes
    to the collective swarm behavior via a shared class-level list.
    """

    # Shared list for tracking all agents
    all_agents = []

    # Speed bounds pulled from config
    max_speed = simulation_config["max_speed"]
    min_speed = simulation_config["min_speed"]

    def __init__(self, position, direction):
        """
        Initialize an Agent with position and normalized direction.

        :param position: Initial 3D position as a list or numpy array.
        :param direction: Initial 3D direction (will be normalized).
        """
        # Store position as NumPy array for vector math
        self.position = np.array(position, dtype=float)

        # Normalize direction vector to unit length
        self.direction = np.array(direction, dtype=float)
        norm = np.linalg.norm(self.direction)
        if norm == 0:
            raise ValueError("Direction vector cannot be zero.")
        self.direction /= norm

        # Random initial speed within bounds
        self.speed = random.uniform(
            simulation_config["init_speed_bounds"][0],
            simulation_config["init_speed_bounds"][1]
        )

        # Register this agent in the global list
        Agent.all_agents.append(self)

    def update_position(self):
        """
        Update this agent's position using the configured movement model.
        """
        model = get_movement_model_by_name(simulation_config["movement_model"])
        model.update_position(self, self.all_agents)
