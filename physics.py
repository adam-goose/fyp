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