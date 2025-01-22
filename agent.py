import random
import numpy as np
from config import simulation_config

class Agent:
    """
    Represents an individual agent in the swarm simulation.

    Each agent has attributes for its position, direction, and speed, as well
    as behaviors for flocking (cohesion, alignment, separation), wall repulsion,
    and movement dynamics. The `Agent` class also maintains a class-level list
    (`all_agents`) to track all instantiated agents.

    Attributes:
        all_agents (list): A class-level variable that stores all instances of the `Agent` class.

    Methods:
        __init__: Initializes an agent with position, direction, and speed.
        calc_movement: Calculates the agent's next movement direction based on flocking behaviors.
        calc_cohesion: Computes a vector that moves the agent toward its neighbors.
        calc_alignment: Computes a vector that aligns the agent with its neighbors' directions.
        calc_separation: Computes a vector that repels the agent from nearby neighbors to avoid crowding.
        calc_wall_repulsion: Computes a vector that repels the agent from the boundaries of the simulation space.
        adjust_speed: Adjusts the agent's speed dynamically based on movement alignment.
        update_position: Updates the agent's position using its current speed and direction.
    """
    # Class level variable to store all agents
    all_agents = []

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

        # Set the desired speed, maximum speed, and minimum speed from simulation_config
        self.desired_speed = simulation_config["desired_speed"] # Assigns desired speed
        self.max_speed = simulation_config["max_speed"] # Assigns the maximum speed
        self.min_speed = simulation_config["min_speed"] # Assigns the minimum speed
        self.speed = random.uniform(simulation_config["init_speed_bounds"][0], simulation_config["init_speed_bounds"][1])
        # Initialise the agent's speed to a random value within the configured bounds

        # Add self to the class level all_agents list
        Agent.all_agents.append(self)

    def calc_cohesion(self, filtered_neighbours):
        """
        Calculate the cohesion vector for the agent based on neighboring agents.

        This method calculates a vector pointing toward the average position
        of neighboring agents that are within the cohesion radius. The resulting
        vector is normalized to indicate direction without affecting magnitude.

        Args:
            filtered_neighbours (list): A list of Agent objects identified as neighbors.

        Returns:
            np.ndarray: A normalized 3D vector pointing toward the average position
            of neighbors within the cohesion radius. Returns a zero vector if no
            neighbors are within range.
        """
        # Initialise the cohesion vector and a counter for neighbours
        cohesion_vector = np.array([0.0, 0.0, 0.0])
        count = 0

        # Use only neighbours within the cohesion radius
        for neighbour in filtered_neighbours:
            distance = np.linalg.norm(neighbour.position - self.position) # Calculate distance to neighbour
            if distance <= simulation_config["cohesion_radius"]: # Check if within cohesion_radius
                cohesion_vector += neighbour.position # Add neighbour's position to the cohesion vector
                count += 1 # Increment neighbour count

        if count > 0:
            # Calculate the average position of neighbours
            average_position = cohesion_vector / count

            # Calculate a vector pointing toward the average position
            cohesion_vector = average_position - self.position

            # Normalise the cohesion vector
            cohesion_vector = cohesion_vector / np.linalg.norm(cohesion_vector)

        return cohesion_vector # Return the final cohesion vector

    def calc_alignment(self, filtered_neighbours):
        """
        Calculate the alignment vector for the agent based on neighboring agents.

        This method computes a vector that aligns the agent's direction with the
        average direction of neighboring agents within the alignment radius. The
        resulting vector is normalized to indicate direction without affecting magnitude.

        Args:
            filtered_neighbours (list): A list of Agent objects identified as neighbors.

        Returns:
            np.ndarray: A normalized 3D vector representing the average alignment
            with neighbors' directions. Returns a zero vector if no neighbors are within range.
        """
        # Initialise the alignment vector and a counter for neighbours
        alignment_vector = np.array([0.0, 0.0, 0.0])
        count = 0

        # Use only neighbours within the alignment radius
        for neighbor in filtered_neighbours:
            # Calculate the distance between the agent and the neighbour
            distance = np.linalg.norm(neighbor.position - self.position)
            if distance <= simulation_config["alignment_radius"]: # Check if within alignment radius
                alignment_vector += neighbor.direction # Add the neighbour's direction to the alignment vector
                count += 1 # Increment neighbour count

        if count > 0:
            # Calculate the average direction of neighbours
            alignment_vector = alignment_vector / count

            # Normalise the alignment vector
            alignment_vector = alignment_vector / np.linalg.norm(alignment_vector)

        return alignment_vector # Return the final alignment vector

    def calc_separation(self, filtered_neighbours):
        """
        Calculate the separation vector for the agent to avoid overcrowding.

        This method computes a vector that repels the agent away from its neighbors
        to maintain a safe distance. The repulsion force is inversely proportional
        to the square of the distance between the agent and its neighbors, ensuring
        stronger repulsion at closer distances. The resulting vector is normalized.

        Args:
            filtered_neighbours (list): A list of Agent objects identified as neighbors.

        Returns:
            np.ndarray: A normalized 3D vector representing the repulsion from neighbors.
            Returns a zero vector if no neighbors are within the separation radius.
        """
        # Initialise the separation vector
        separation_vector = np.array([0.0, 0.0, 0.0])

        # Iterate over filtered neighbors
        for neighbor in filtered_neighbours:
            # Calculate the distance between the agent and the neighbour
            distance = np.linalg.norm(neighbor.position - self.position)

            # Avoid division by zero and only consider neghbours within the separation radius
            if 0 < distance <= simulation_config["separation_radius"]:
                # Calculate the repulsion vector (inverse of the distance squared)
                repulsion = (self.position - neighbor.position) / (distance ** 2)
                separation_vector += repulsion # Add the repulsion to the separation vector

        # Normalize the resulting separation vector if it has any magnitude
        if np.linalg.norm(separation_vector) > 0:
            separation_vector = separation_vector / np.linalg.norm(separation_vector)

        return separation_vector # Return the normalised separation vector

    def get_neighbours_within_radius(self):
        """
        Find all neighboring agents within the perception radius of this agent.

        This method iterates through all agents in the simulation and calculates
        the distance between the current agent and others. It returns a list of
        agents that are within the defined perception radius, excluding the agent itself.

        Returns:
            list: A list of Agent objects that are within the perception radius.
        """
        neighbours = [] # Initialises an empty list to store neighbouring agents

        for agent in Agent.all_agents:  # Access all agents in the simulation
            if agent is not self:  # Exclude the current agent itself
                # Calculate the distance between the agent and the current agent
                distance = np.linalg.norm(self.position - agent.position)

                # Check if the distance is within the perception radius
                if distance <= simulation_config["perception_radius"]:
                    neighbours.append(agent) # Add the agent to the neighbours list

        return neighbours # Return the list of neighbours

    def adjust_speed(self, combined_vector):
        """
        Adjust the agent's speed dynamically based on alignment with the desired movement.

        This method calculates the alignment between the agent's current direction
        (momentum) and the new desired direction (combined_vector) using the dot
        product. If the alignment is high, the agent accelerates smoothly toward its
        desired speed. Otherwise, the agent decelerates proportionally to the misalignment.
        This makes the agents slow down when turning and speed up when flying steadily.

        Args:
            combined_vector (np.ndarray): The desired movement vector after considering
            cohesion, alignment, separation, and other forces.

        Returns:
            None: The agent's speed is updated in place.
        """
        # Calculate the dot product of current momentum and the combined vector
        alignment = np.dot(self.direction, combined_vector)  # Dot product for alignment
        alignment = max(-1, min(1, alignment))  # Clamp to [-1, 1]

        # If alignment is high, accelerate toward desired speed
        if alignment > 0.9:  # If nearly aligned
            self.speed += (self.desired_speed - self.speed) * 0.01  # Smooth acceleration
        else:  # If not aligned, reduce speed
            self.speed -= abs((1 - alignment)) * 0.05  # Deceleration penalty

        # Clamp the speed to a valid range
        self.speed = max(self.min_speed, min(self.max_speed, self.speed))

    @staticmethod
    def calculate_boundary_repulsion(position, min_boundary, max_boundary, threshold, max_force):
        """
        Calculate the repulsion force for a position based on proximity to both min and max boundaries.

        Args:
            position (float): Current position along an axis.
            min_boundary (float): The minimum boundary for the axis.
            max_boundary (float): The maximum boundary for the axis.
            threshold (float): Distance threshold at which the repulsion force starts applying.
            max_force (float): The maximum repulsion force applied when the position is at the boundary.

        Returns:
            float: The calculated repulsion force for this axis.
        """
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

    def calc_wall_repulsion(self):
        """
        Calculate the total wall repulsion force for all boundaries using a generalised function.

        Returns:
            np.ndarray: A 3D vector representing the repulsion force from walls.
        """

        repulsion_force = np.array([
            Agent.calculate_boundary_repulsion(
                self.position[0],
                simulation_config["x_min"],
                simulation_config["x_max"],
                simulation_config["boundary_threshold"],
                simulation_config["boundary_max_force"]
            ),
            Agent.calculate_boundary_repulsion(
                self.position[1],
                simulation_config["y_min"],
                simulation_config["y_max"],
                simulation_config["boundary_threshold"],
                simulation_config["boundary_max_force"]
            ),
            Agent.calculate_boundary_repulsion(
                self.position[2],
                simulation_config["z_min"],
                simulation_config["z_max"],
                simulation_config["boundary_threshold"],
                simulation_config["boundary_max_force"]
            )
        ])

        return repulsion_force  # Returns the repulsion force vector

    def calc_movement(self):
        """
        Calculate the agent's new movement vector based on flocking behaviors and environmental constraints.

        This method computes the combined influence of cohesion, alignment, separation,
        momentum, and wall repulsion forces. The forces are weighted and combined to
        determine the agent's next movement direction. The final vector is normalized
        to ensure uniform movement magnitude.

        Returns:
            np.ndarray: A normalized 3D vector representing the agent's new direction.
        """
        # Pre-filter neighbors once based on the maximum perception radius
        filtered_neighbors = self.get_neighbours_within_radius()

        # Calculate individual behaviors based on filtered neighbours
        cohesion_vector = self.calc_cohesion(filtered_neighbors)
        alignment_vector = self.calc_alignment(filtered_neighbors)
        separation_vector = self.calc_separation(filtered_neighbors)

        # Calculate current momentum (direction * speed) and wall repulsion force
        current_momentum = self.direction * self.speed  # Current momentum vector
        wall_repulsion_vector = self.calc_wall_repulsion()  # Repulsion force from walls

        # Combine vectors with respective weights from simulation configuration
        combined_vector = (
                simulation_config["cohesion_weight"] * cohesion_vector +
                simulation_config["alignment_weight"] * alignment_vector +
                simulation_config["separation_weight"] * separation_vector +
                simulation_config["momentum_weight"] * current_momentum +
                simulation_config["wall_repulsion_weight"] * wall_repulsion_vector
        )

        # Normalize the final movement vector if it has non-zero magnitude
        if np.linalg.norm(combined_vector) > 0:
            combined_vector = combined_vector / np.linalg.norm(combined_vector)

        # Adjust the agent's speed based on the combined movement vector
        self.adjust_speed(combined_vector)

        return combined_vector  # Return the normalised movement vector

    def update_position(self):
        """
        Update the agent's position based on its calculated movement vector and speed.

        This method calculates the agent's new direction using `calc_movement()`,
        then updates its position by applying the direction, speed, and a time step
        (`delta_time` from the simulation configuration).

        Returns:
            None: The agent's position is updated in place.
        """
        # The calculated combined vector from calc_movement is the agent's new direction
        self.direction = self.calc_movement()

        # Update position using the new direction, current speed, and time step
        self.position += self.direction * self.speed * simulation_config["delta_time"]
