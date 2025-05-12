import numpy as np
from config import simulation_config

class WallPhysics:
    """
    Handles wall-based repulsion forces based on the agent's proximity
    to the defined bounding box of the simulation space.
    """

    @staticmethod
    def calculate_boundary_repulsion(position, min_boundary, max_boundary):
        """
        Calculate 1D repulsion force based on proximity to either end of the boundary.

        :param position: Current coordinate value of the agent along one axis.
        :param min_boundary: Lower bound of the simulation space on that axis.
        :param max_boundary: Upper bound of the simulation space on that axis.
        :return: A scalar repulsion force (positive if too close to min, negative if too close to max).
        """
        threshold = simulation_config["boundary_threshold"]
        max_force = simulation_config["boundary_max_force"]

        # Repel if too close to the minimum boundary
        if position < min_boundary + threshold:
            distance = position - min_boundary
            return max_force * (threshold - distance) / threshold

        # Repel if too close to the maximum boundary
        elif position > max_boundary - threshold:
            distance = max_boundary - position
            return -max_force * (threshold - distance) / threshold

        # No repulsion needed within safe bounds
        return 0.0

    @staticmethod
    def calc_wall_repulsion(current_agent):
        """
        Calculate a 3D vector representing total repulsion from all simulation walls.

        :param current_agent: The agent being repelled.
        :return: A numpy array (3,) representing repulsion forces along x, y, z axes.
        """
        pos = current_agent.position

        # Compute repulsion independently for each axis
        return np.array([
            WallPhysics.calculate_boundary_repulsion(pos[0], simulation_config["x_min"], simulation_config["x_max"]),
            WallPhysics.calculate_boundary_repulsion(pos[1], simulation_config["y_min"], simulation_config["y_max"]),
            WallPhysics.calculate_boundary_repulsion(pos[2], simulation_config["z_min"], simulation_config["z_max"])
        ])


class ObstaclePhysics:
    """
    Handles repulsion force calculations between agents and static rectangular obstacles.
    """

    @staticmethod
    def calculate_obstacle_repulsion(agent_position, threshold, max_force):
        """
        Calculate a repulsion force based on distance from a box-shaped obstacle.

        :param agent_position: The agent's current position (3D vector).
        :param threshold: Distance around the obstacle in which repulsion is active.
        :param max_force: Maximum repulsion force applied at zero distance.
        :return: A 3D numpy array representing the repulsion vector.
        """
        if not simulation_config.get("obstacle_enabled", False):
            return np.zeros(3)

        # Get obstacle corners from config
        obstacle_min = np.array(simulation_config["obstacle_corner_min"], dtype=float)
        obstacle_max = np.array(simulation_config["obstacle_corner_max"], dtype=float)

        # Ensure consistent bounding box regardless of min/max order
        min_corner = np.minimum(obstacle_min, obstacle_max)
        max_corner = np.maximum(obstacle_min, obstacle_max)

        pos = np.array(agent_position)

        # Define the outer threshold region around the obstacle
        expanded_min = min_corner - threshold
        expanded_max = max_corner + threshold

        # If agent is outside the threshold zone, no force is applied
        if np.any(pos < expanded_min) or np.any(pos > expanded_max):
            return np.zeros(3)

        # Clamp position to obstacle bounds to find closest surface point
        closest = np.maximum(min_corner, np.minimum(pos, max_corner))
        offset = pos - closest
        distance = np.linalg.norm(offset)

        if distance == 0:
            # Agent is inside the obstacle - push outwards from center
            center = (min_corner + max_corner) / 2
            fallback = pos - center
            if np.linalg.norm(fallback) == 0:
                # Fallback to a random direction if perfectly centered
                fallback = np.random.uniform(-1, 1, 3)
            return max_force * fallback / np.linalg.norm(fallback)

        # Scale force based on proximity to obstacle surface
        force_strength = max_force * (threshold - distance) / threshold
        return force_strength * (offset / distance)
