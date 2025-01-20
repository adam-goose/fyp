import numpy as np
from config import simulation_config

class Agent:
    # Class level variable to store all agents
    all_agents = []

    def __init__(self, position, direction, speed):
        self.position = np.array(position, dtype=float) # Ensure position is a numpy array
        self.direction = np.array(direction, dtype=float) # Ensure direction is a numpy array
        self.direction = self.direction / np.linalg.norm(self.direction) # Normalise direction to make it a unit vector
        self.desired_speed = simulation_config["desired_speed"] # Assigns desired speed
        self.max_speed = simulation_config["max_speed"] # Assigns the maximum speed
        self.min_speed = simulation_config["min_speed"] # Assigns the minimum speed
        self.speed = speed # Assign actual speed

        # Add self to the class level all_agents list
        Agent.all_agents.append(self)

    def calc_cohesion(self, filtered_neighbours):
        cohesion_vector = np.array([0.0, 0.0, 0.0])
        count = 0

        # Use only neighbours within the cohesion radius
        for neighbour in filtered_neighbours:
            distance = np.linalg.norm(neighbour.position - self.position) # Distance is neighbour's position subtract own position
            if distance <= simulation_config["cohesion_radius"]: # If within cohesion radius then add its position to the cohesion vector
                cohesion_vector += neighbour.position
                count += 1

        if count > 0:
            # Calculate the average position of neighbours
            average_position = cohesion_vector / count

            # Point towards the average position
            cohesion_vector = average_position - self.position

            # Normalise the cohesion vector
            cohesion_vector = cohesion_vector / np.linalg.norm(cohesion_vector)

        return cohesion_vector

    def calc_alignment(self, filtered_neighbours):
        alignment_vector = np.array([0.0, 0.0, 0.0])
        count = 0

        # Use only neighbours within the alignment radius
        for neighbor in filtered_neighbours:
            distance = np.linalg.norm(neighbor.position - self.position)
            if distance <= simulation_config["alignment_radius"]:
                alignment_vector += neighbor.direction
                count += 1

        if count > 0:
            # Calculate the average direction
            alignment_vector = alignment_vector / count

            # Normalise the alignment vector
            alignment_vector = alignment_vector / np.linalg.norm(alignment_vector)

        return alignment_vector

    def calc_separation(self, filtered_neighbours):
        separation_vector = np.array([0.0, 0.0, 0.0])

        # Iterate over filtered neighbors
        for neighbor in filtered_neighbours:
            distance = np.linalg.norm(neighbor.position - self.position)

            if 0 < distance <= simulation_config["separation_radius"]:  # Avoid division by zero for identical positions
                # Calculate the repulsion vector (inverse of the distance)
                repulsion = (self.position - neighbor.position) / (distance ** 2)
                separation_vector += repulsion

        # Normalize the resulting separation vector if it has any effect
        if np.linalg.norm(separation_vector) > 0:
            separation_vector = separation_vector / np.linalg.norm(separation_vector)

        return separation_vector

    def get_neighbours_within_radius(self):
        neighbours = []
        for agent in Agent.all_agents:  # Access all agents in the simulation
            if agent is not self:  # Exclude self
                distance = np.linalg.norm(self.position - agent.position)
                if distance <= simulation_config["perception_radius"]:
                    neighbours.append(agent)
        return neighbours

    def adjust_speed(self, combined_vector):
        """
        Adjust the agent's speed based on the alignment of the current momentum
        with the desired movement (combined vector).
        """
        # Calculate the dot product of current momentum and the combined vector
        alignment = np.dot(self.direction, combined_vector)  # Dot product for alignment
        alignment = max(-1, min(1, alignment))  # Clamp to [-1, 1]

        # If alignment is high, accelerate toward desired speed
        if alignment > 0.9:  # Nearly aligned
            self.speed += (self.desired_speed - self.speed) * 0.01  # Smooth acceleration
        else:  # If not aligned, reduce speed
            self.speed -= abs((1 - alignment)) * 0.5  # Deceleration penalty

        # Clamp the speed to a valid range
        self.speed = max(self.min_speed, min(self.max_speed, self.speed))

    def calc_wall_repulsion(self):
        repulsion_force = np.array([0.0, 0.0, 0.0])  # Initialize to zero
        threshold = 2.0  # Distance threshold to trigger repulsion

        # Check against each boundary
        if self.position[0] < simulation_config["x_min"] + threshold:
            repulsion_force[0] += 1 / (self.position[0] - simulation_config["x_min"] + 0.1)  # Push away from x_min
        if self.position[0] > simulation_config["x_max"] - threshold:
            repulsion_force[0] -= 1 / (simulation_config["x_max"] - self.position[0] + 0.1)  # Push away from x_max

        if self.position[1] < simulation_config["y_min"] + threshold:
            repulsion_force[1] += 1 / (self.position[1] - simulation_config["y_min"] + 0.1)  # Push away from y_min
        if self.position[1] > simulation_config["y_max"] - threshold:
            repulsion_force[1] -= 1 / (simulation_config["y_max"] - self.position[1] + 0.1)  # Push away from y_max

        if self.position[2] < simulation_config["z_min"] + threshold:
            repulsion_force[2] += 1 / (self.position[2] - simulation_config["z_min"] + 0.1)  # Push away from z_min
        if self.position[2] > simulation_config["z_max"] - threshold:
            repulsion_force[2] -= 1 / (simulation_config["z_max"] - self.position[2] + 0.1)  # Push away from z_max

        return repulsion_force

    def calc_movement(self):
        # Pre-filter neighbors once based on the maximum perception radius
        filtered_neighbors = self.get_neighbours_within_radius()

        # Calculate individual behaviors
        cohesion_vector = self.calc_cohesion(filtered_neighbors)
        alignment_vector = self.calc_alignment(filtered_neighbors)
        separation_vector = self.calc_separation(filtered_neighbors)

        # Calculate current momentum (direction * speed)
        current_momentum = self.direction * self.speed
        wall_repulsion_vector = self.calc_wall_repulsion()

        # Combine vectors with weights
        combined_vector = (
                simulation_config["cohesion_weight"] * cohesion_vector +
                simulation_config["alignment_weight"] * alignment_vector +
                simulation_config["separation_weight"] * separation_vector +
                simulation_config["momentum_weight"] * current_momentum +
                simulation_config["wall_repulsion_weight"] * wall_repulsion_vector
        )

        # Normalize the final movement vector
        if np.linalg.norm(combined_vector) > 0:
            combined_vector = combined_vector / np.linalg.norm(combined_vector)

        self.adjust_speed(combined_vector)

        return combined_vector

    def update_position(self):
        # The calculated combined vector from calc_movement is the agent's new direction
        self.direction = self.calc_movement()

        # Update position using the direction and speed
        self.position += self.direction * self.speed * simulation_config["delta_time"]
