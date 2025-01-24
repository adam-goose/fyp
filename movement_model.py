from config import simulation_config
import config
from agent import Agent
from physics import *
import numpy as np

class MovementModel:
    """
    Base class for movement models.
    """
    def calc_movement(self, current_agent, all_agents):
        raise NotImplementedError("Subclasses must implement calc_movement")

class Boids(MovementModel):
    """

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
    @staticmethod
    def get_neighbours_within_radius(current_agent):
        """
        Find all neighboring agents within the perception radius of this agent.

        This method iterates through all agents in the simulation and calculates
        the distance between the current agent and others. It returns a list of
        agents that are within the defined perception radius, excluding the agent itself.

        Args:
            current_agent (Agent): The current agent performing movement model calculations.

        Returns:
            list: A list of Agent objects that are within the perception radius.
        """
        neighbours = [] # Initialises an empty list to store neighbouring agents

        for agent in Agent.all_agents:  # Access all agents in the simulation
            if agent is not current_agent:  # Exclude the current agent itself
                # Calculate the distance between the agent and the current agent
                distance = np.linalg.norm(current_agent.position - agent.position)

                # Check if the distance is within the perception radius
                if distance <= simulation_config["perception_radius"]:
                    neighbours.append(agent) # Add the agent to the neighbours list

        return neighbours # Return the list of neighbours

    @staticmethod
    def calc_cohesion(filtered_neighbours, current_agent):
        """
        Calculate the cohesion vector for the agent based on neighboring agents.

        This method calculates a vector pointing toward the average position
        of neighboring agents that are within the cohesion radius. The resulting
        vector is normalized to indicate direction without affecting magnitude.

        Args:
            filtered_neighbours (list): A list of Agent objects identified as neighbors.
            current_agent (Agent): The current agent performing movement model calculations.

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
            distance = np.linalg.norm(neighbour.position - current_agent.position) # Calculate distance to neighbour
            if distance <= simulation_config["cohesion_radius"]: # Check if within cohesion_radius
                cohesion_vector += neighbour.position # Add neighbour's position to the cohesion vector
                count += 1 # Increment neighbour count

        if count > 0:
            # Calculate the average position of neighbours
            average_position = cohesion_vector / count

            # Calculate a vector pointing toward the average position
            cohesion_vector = average_position - current_agent.position

            # Normalise the cohesion vector
            cohesion_vector = cohesion_vector / np.linalg.norm(cohesion_vector)

        return cohesion_vector # Return the final cohesion vector

    @staticmethod
    def calc_alignment(filtered_neighbours, current_agent):
        """
        Calculate the alignment vector for the agent based on neighboring agents.

        This method computes a vector that aligns the agent's direction with the
        average direction of neighboring agents within the alignment radius. The
        resulting vector is normalized to indicate direction without affecting magnitude.

        Args:
            filtered_neighbours (list): A list of Agent objects identified as neighbors.
            current_agent (Agent): The current agent performing movement model calculations.

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
            distance = np.linalg.norm(neighbor.position - current_agent.position)
            if distance <= simulation_config["alignment_radius"]: # Check if within alignment radius
                alignment_vector += neighbor.direction # Add the neighbour's direction to the alignment vector
                count += 1 # Increment neighbour count

        if count > 0:
            # Calculate the average direction of neighbours
            alignment_vector = alignment_vector / count

            # Normalise the alignment vector
            alignment_vector = alignment_vector / np.linalg.norm(alignment_vector)

        return alignment_vector # Return the final alignment vector

    @staticmethod
    def calc_separation(filtered_neighbours, current_agent):
        """
        Calculate the separation vector for the agent to avoid overcrowding.

        This method computes a vector that repels the agent away from its neighbors
        to maintain a safe distance. The repulsion force is inversely proportional
        to the square of the distance between the agent and its neighbors, ensuring
        stronger repulsion at closer distances. The resulting vector is normalized.

        Args:
            filtered_neighbours (list): A list of Agent objects identified as neighbors.
            current_agent (Agent): The current agent performing movement model calculations.

        Returns:
            np.ndarray: A normalized 3D vector representing the repulsion from neighbors.
            Returns a zero vector if no neighbors are within the separation radius.
        """
        # Initialise the separation vector
        separation_vector = np.array([0.0, 0.0, 0.0])

        # Iterate over filtered neighbors
        for neighbor in filtered_neighbours:
            # Calculate the distance between the agent and the neighbour
            distance = np.linalg.norm(neighbor.position - current_agent.position)

            # Avoid division by zero and only consider neghbours within the separation radius
            if 0 < distance <= simulation_config["separation_radius"]:
                # Calculate the repulsion vector (inverse of the distance squared)
                repulsion = (current_agent.position - neighbor.position) / (distance ** 2)
                separation_vector += repulsion # Add the repulsion to the separation vector

        # Normalize the resulting separation vector if it has any magnitude
        if np.linalg.norm(separation_vector) > 0:
            separation_vector = separation_vector / np.linalg.norm(separation_vector)

        return separation_vector # Return the normalised separation vector

    @staticmethod
    def adjust_speed(combined_vector, current_agent):
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
            current_agent (Agent): The current agent performing movement model calculations.

        Returns:
            None: The agent's speed is updated in place.
        """
        # Calculate the dot product of current momentum and the combined vector
        heading_alignment = np.dot(current_agent.direction, combined_vector)  # Dot product for alignment
        heading_alignment = max(-1, min(1, heading_alignment))  # Clamp to [-1, 1]

        # If alignment is high, accelerate toward desired speed
        if heading_alignment > simulation_config["heading_alignment_threshold"]:  # If nearly aligned
            current_agent.speed += (current_agent.desired_speed - current_agent.speed) * simulation_config["acceleration"]  # Smooth acceleration
        else:  # If not aligned, reduce speed
            current_agent.speed -= abs((1 - heading_alignment)) * simulation_config["deceleration"]  # Deceleration penalty

        # Clamp the speed to a valid range
        current_agent.speed = max(current_agent.min_speed, min(current_agent.max_speed, current_agent.speed))

    def calc_movement(self, current_agent, all_agents):
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
        filtered_neighbors = Boids.get_neighbours_within_radius(current_agent)

        # Calculate individual behaviors based on filtered neighbours
        cohesion_vector = Boids.calc_cohesion(filtered_neighbors, current_agent)
        alignment_vector = Boids.calc_alignment(filtered_neighbors, current_agent)
        separation_vector = Boids.calc_separation(filtered_neighbors, current_agent)

        # Calculate current momentum (direction * speed) and wall repulsion force
        current_momentum = current_agent.direction * current_agent.speed  # Current momentum vector
        wall_repulsion_vector = WallPhysics.calc_wall_repulsion(current_agent)  # Repulsion force from walls

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
        self.adjust_speed(combined_vector, current_agent)

        return combined_vector  # Return the normalised movement vector