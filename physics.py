import numpy as np
from config import simulation_config
class WallPhysics:

    @staticmethod
    def calculate_boundary_repulsion(position, min_boundary, max_boundary):
        """
        Calculate the repulsion force for a position based on proximity to both min and max boundaries.

        Args:
            position (float): Current position along an axis.
            min_boundary (float): The minimum boundary for the axis.
            max_boundary (float): The maximum boundary for the axis.

        Returns:
            float: The calculated repulsion force for this axis.
        """
        threshold = simulation_config["boundary_threshold"]
        max_force = simulation_config["boundary_max_force"]

        if position < min_boundary + threshold:
            # If the position is close to or beyond the minimum boundary:
            # Calculate the distance from the agent to the min boundary.
            distance = position - min_boundary

            # The repulsion force increases linearly as the agent gets closer
            # to the min boundary, reaching max_force when distance is 0
            # and more than max force when the agent leaves the boundary.
            return max_force * (threshold - distance) / threshold

        elif position > max_boundary - threshold:
            # If the position is close to or beyond the maximum boundary:
            # Calculate the distance from the agent to the max boundary.
            distance = max_boundary - position

            # The repulsion force increases linearly as the agent gets closer
            # to the max boundary, reaching -max_force when distance is 0
            # and more than max force when the agent leaves the boundary.
            return -max_force * (threshold - distance) / threshold

        else:
            # If the agent is within the safe bounds, no repulsion force is applied.
            return 0.0

    @staticmethod
    def calc_wall_repulsion(current_agent):
        """
        Calculate the total wall repulsion force for all boundaries using a generalised function.

        Returns:
            np.ndarray: A 3D vector representing the repulsion force from walls.
        """

        repulsion_force = np.array([
            WallPhysics.calculate_boundary_repulsion(
                current_agent.position[0],
                simulation_config["x_min"],
                simulation_config["x_max"]
            ),
            WallPhysics.calculate_boundary_repulsion(
                current_agent.position[1],
                simulation_config["y_min"],
                simulation_config["y_max"]
            ),
            WallPhysics.calculate_boundary_repulsion(
                current_agent.position[2],
                simulation_config["z_min"],
                simulation_config["z_max"]
            )
        ])

        return repulsion_force  # Returns the repulsion force vector


class ObstaclePhysics:

    @staticmethod
    def calculate_obstacle_repulsion(agent_position, threshold, max_force):
        if not simulation_config.get("obstacle_enabled", False):
            return np.array([0.0, 0.0, 0.0])

        obstacle_min = np.array(simulation_config["obstacle_corner_min"], dtype=float)
        obstacle_max = np.array(simulation_config["obstacle_corner_max"], dtype=float)

        # Compute the minimum and maximum corners correctly
        min_corner = np.minimum(obstacle_min, obstacle_max)
        max_corner = np.maximum(obstacle_min, obstacle_max)

        agent_position = np.array(agent_position)

        # Inflate obstacle boundaries by threshold to create repulsion zone
        expanded_min = min_corner - threshold
        expanded_max = max_corner + threshold

        # If outside the repulsion zone, no force
        if np.any(agent_position < expanded_min) or np.any(agent_position > expanded_max):
            return np.array([0.0, 0.0, 0.0])

        # Clamp to find closest point on obstacle
        closest_point = np.maximum(min_corner, np.minimum(agent_position, max_corner))
        vector_to_agent = agent_position - closest_point
        distance = np.linalg.norm(vector_to_agent)

        if distance == 0:
            # Agent is inside the obstacle
            center = (min_corner + max_corner) / 2
            direction = agent_position - center
            if np.linalg.norm(direction) == 0:
                direction = np.random.uniform(-1, 1, 3)
            return max_force * direction / np.linalg.norm(direction)

        # Within threshold around the obstacle
        force_magnitude = max_force * (threshold - distance) / threshold
        return force_magnitude * (vector_to_agent / distance)
