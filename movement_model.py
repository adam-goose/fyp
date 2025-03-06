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
    def get_neighbours_within_radius(current_agent, all_agents=None, perception_radius=None):
        """
        Find all neighboring agents within the perception radius of this agent.

        This method iterates through all agents in the simulation and calculates
        the distance between the current agent and others. It returns a list of
        agents that are within the defined perception radius, excluding the agent itself.

        Args:
            current_agent (Agent): The current agent performing the neighbor search.
            all_agents (list[Agent], optional): The list of agents to search through.
                Defaults to Agent.all_agents if not provided.
            perception_radius (float, optional): The maximum distance within which
                an agent is considered a neighbor. If None, defaults to the global
                value in simulation_config["perception_radius"].

        Returns:
            list[Agent]: A list of Agent objects that are within the perception radius.
        """
        neighbours = [] # Initialises an empty list to store neighbouring agents

        if all_agents is None:
            all_agents = Agent.all_agents  # Default to global list of all agents

        if perception_radius is None:
            perception_radius = simulation_config["perception_radius"]  # Use global config if radius is not passed

        for agent in all_agents:  # Access all agents in the simulation
            if agent is not current_agent:  # Exclude the current agent itself
                # Calculate the distance between the agent and the current agent
                distance = np.linalg.norm(current_agent.position - agent.position)

                # Check if the distance is within the perception radius
                if distance <= perception_radius:
                    neighbours.append(agent) # Add the agent to the neighbours list

        return neighbours # Return the list of neighbours


    @staticmethod
    def calc_cohesion(filtered_neighbours, current_agent, cohesion_radius=None):
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

        if cohesion_radius is None:
            cohesion_radius = simulation_config["cohesion_radius"]

        # Use only neighbours within the cohesion radius
        for neighbour in filtered_neighbours:
            distance = np.linalg.norm(neighbour.position - current_agent.position) # Calculate distance to neighbour
            if distance <= cohesion_radius: # Check if within cohesion_radius
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
    def calc_alignment(filtered_neighbours, current_agent, alignment_radius=None):
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

        if alignment_radius is None:
            alignment_radius = simulation_config["alignment_radius"]

        # Use only neighbours within the alignment radius
        for neighbor in filtered_neighbours:
            # Calculate the distance between the agent and the neighbour
            distance = np.linalg.norm(neighbor.position - current_agent.position)
            if distance <= alignment_radius: # Check if within alignment radius
                alignment_vector += neighbor.direction # Add the neighbour's direction to the alignment vector
                count += 1 # Increment neighbour count

        if count > 0:
            # Calculate the average direction of neighbours
            alignment_vector = alignment_vector / count

            # Normalise the alignment vector
            alignment_vector = alignment_vector / np.linalg.norm(alignment_vector)

        return alignment_vector # Return the final alignment vector


    @staticmethod
    def calc_separation(filtered_neighbours, current_agent, separation_radius=None):
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

        if separation_radius is None:
            separation_radius = simulation_config["separation_radius"]

        # Iterate over filtered neighbors
        for neighbor in filtered_neighbours:
            # Calculate the distance between the agent and the neighbour
            distance = np.linalg.norm(neighbor.position - current_agent.position)

            # Avoid division by zero and only consider neghbours within the separation radius
            if 0 < distance <= separation_radius:
                # Calculate the repulsion vector (inverse of the distance squared)
                repulsion = (current_agent.position - neighbor.position) / (distance ** 2)
                separation_vector += repulsion # Add the repulsion to the separation vector

        # Normalize the resulting separation vector if it has any magnitude
        if np.linalg.norm(separation_vector) > 0:
            separation_vector = separation_vector / np.linalg.norm(separation_vector)

        return separation_vector # Return the normalised separation vector


    def update_position(self, current_agent, all_agents):
        self.adjust_speed(current_agent)

        velocity = current_agent.direction * current_agent.speed * simulation_config["momentum_weight"]

        # Update position using the new direction, current speed, and time step
        current_agent.position += velocity * 0.01


    def adjust_speed(self, current_agent):

        # Compute the desired target speed
        target_speed = self.calc_speed(current_agent)

        # If target speed is lower than current speed, decelerate smoothly
        if target_speed < current_agent.speed:
            speed_change = (current_agent.speed - target_speed) * (1 - np.exp(-simulation_config["deceleration"]))
            current_agent.speed -= speed_change
        else:
            # Normal acceleration logic
            speed_change = (target_speed - current_agent.speed) * (1 - np.exp(-simulation_config["acceleration"]))
            current_agent.speed += speed_change

        # Clamp speed between min and max
        current_agent.speed = max(current_agent.min_speed, min(simulation_config["max_speed"], current_agent.speed))


    def calc_speed(self, current_agent):
        old_direction = self.adjust_direction(current_agent)

        # Compute the angle between current and desired direction
        alignment = np.dot(current_agent.direction, old_direction)
        alignment = np.clip(alignment, -1, 1)
        turn_angle = np.arccos(alignment)


        # Define a small threshold for "going straight" (in radians)
        straight_threshold = np.radians(simulation_config["turn_sensitivity"])  # Adjust this as needed

        if turn_angle <= straight_threshold:
            # Going nearly straight: full forward speed.
            return simulation_config["max_speed"]
        else:
            # Turning: return a negative target speed to trigger deceleration.
            return -abs(simulation_config["max_speed"])


    def adjust_direction(self, current_agent):
        # Normalize vectors to ensure unit length
        current_direction = current_agent.direction / np.linalg.norm(current_agent.direction)
        combined_vector = self.calc_direction(current_agent)

        new_direction = (1 - simulation_config["direction_alpha"]) * current_direction + simulation_config[
            "direction_alpha"] * combined_vector


        # Normalize again to maintain unit vector
        new_direction = new_direction / np.linalg.norm(new_direction)
        old_direction = current_agent.direction
        current_agent.direction = new_direction

        return old_direction


    @staticmethod
    def calc_direction(current_agent):
        # Pre-filter neighbors once based on the maximum perception radius
        filtered_neighbors = Boids.get_neighbours_within_radius(current_agent)

        # Calculate individual behaviors based on filtered neighbours
        cohesion_vector = Boids.calc_cohesion(filtered_neighbors, current_agent)
        alignment_vector = Boids.calc_alignment(filtered_neighbors, current_agent)
        separation_vector = Boids.calc_separation(filtered_neighbors, current_agent)

        # Calculate wall repulsion force
        wall_repulsion_vector = WallPhysics.calc_wall_repulsion(current_agent)  # Repulsion force from walls

        # Combine vectors with respective weights from simulation configuration
        combined_vector = (
                simulation_config["cohesion_weight"] * cohesion_vector +
                simulation_config["alignment_weight"] * alignment_vector +
                simulation_config["separation_weight"] * separation_vector +
                simulation_config["wall_repulsion_weight"] * wall_repulsion_vector
        )

        # Check if the combined vector is zero or near-zero
        vector_magnitude = np.linalg.norm(combined_vector)
        if vector_magnitude < 1e-6:  # Threshold for near-zero magnitude
            # Replace the zero vector with a random unit vector
            combined_vector = current_agent.direction

        combined_vector = combined_vector / np.linalg.norm(combined_vector)

        return combined_vector


