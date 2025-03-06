import random
import numpy as np
from config import *

class Agent:
    """
    Represents an individual agent in the swarm simulation.

    Each agent has attributes for its position, direction, and speed, as well
    as behaviors for flocking (cohesion, alignment, separation), wall repulsion,
    and movement dynamics. The `Agent` class also maintains a class-level list
    (`all_agents`) to track all instantiated agents.

    Attributes:
        all_agents (list): A class-level variable that stores all instances of the `Agent` class.

    """
    # Class level variables
    all_agents = [] # Stores all agents in a list
    max_speed = simulation_config["max_speed"]  # Assigns the maximum speed
    min_speed = simulation_config["min_speed"]  # Assigns the minimum speed


    def __init__(self, position, direction):
        """
        Initialize an Agent instance with position and direction.

        This constructor sets up the agent's position and direction,
        normalizes the direction to a unit vector, and initializes other
        attributes like desired, initial speed bounds, maximum, and
        minimum speeds based on the simulation configuration.

        Args:
            position (list or np.ndarray): The initial position of the agent as a 3D vector [x, y, z].
            direction (list or np.ndarray): The initial movement direction of the agent as a 3D vector.

        Raises:
            ValueError: If the direction vector has zero magnitude and cannot be normalized.
        """
        # Convert the position to a numpy array to allow vector operations
        self.position = np.array(position, dtype=float) # Ensure position is a numpy array

        # Convert the direction to a numpy array and normalise it to a unit vector
        self.direction = np.array(direction, dtype=float) # Ensure direction is a numpy array
        self.direction = self.direction / np.linalg.norm(self.direction) # Normalise direction to make it a unit vector
        self.speed = random.uniform(simulation_config["init_speed_bounds"][0], simulation_config["init_speed_bounds"][1])
        # Initialise the agent's speed to a random value within the configured bounds

        # Add self to the class level all_agents list
        Agent.all_agents.append(self)


    def update_position(self):
        """
        Update the agent's position based on its calculated movement vector and speed.

        This method calculates the agent's new direction using `calc_movement()`,
        then updates its position by applying the direction, speed, and a time step
        (`delta_time` from the simulation configuration).

        Returns:
            None: The agent's position is updated in place.
        """

        get_movement_model_by_name(simulation_config["movement_model"]).update_position(self, self.all_agents)

