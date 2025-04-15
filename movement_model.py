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
    # Class attributes
    buffer_size = 200
    positions = np.zeros((buffer_size, 3))
    directions = np.zeros((buffer_size, 3))
    deltas = np.zeros((buffer_size, 3))
    distances = np.zeros(buffer_size)
    speeds = np.zeros(buffer_size)

    @staticmethod
    def precompute_agent_data(current_agent, all_agents):
        n = len(all_agents)

        if n > Boids.buffer_size:
            Boids.resize_buffers(n)

        Boids.positions[:n] = [a.position for a in all_agents]
        Boids.directions[:n] = [a.direction for a in all_agents]
        Boids.speeds[:n] = [a.speed for a in all_agents]
        current_position = current_agent.position

        Boids.deltas[:n] = Boids.positions[:n] - current_position
        Boids.distances[:n] = np.linalg.norm(Boids.deltas[:n], axis=1)

        return Boids.positions[:n], Boids.directions[:n], Boids.deltas[:n], Boids.distances[:n]

    @staticmethod
    def batch_update_positions(all_agents):
        n = len(all_agents)

        # Resize buffers if needed
        if n > Boids.buffer_size:
            Boids.resize_buffers(n)

        # Fill positions, directions, and speeds
        for i, agent in enumerate(all_agents):
            Boids.positions[i] = agent.position
            Boids.directions[i] = agent.direction
            Boids.speeds[i] = agent.speed

        # Compute new positions in batch
        velocities = Boids.directions[:n] * Boids.speeds[:n, None]
        Boids.positions[:n] += velocities * 0.1  # assuming timestep is 0.1 like before

        # Write updated positions back to agents
        for i, agent in enumerate(all_agents):
            agent.position = Boids.positions[i]

    @staticmethod
    def resize_buffers(new_size):
        Boids.buffer_size = new_size
        Boids.positions = np.zeros((new_size, 3))
        Boids.directions = np.zeros((new_size, 3))
        Boids.deltas = np.zeros((new_size, 3))
        Boids.distances = np.zeros(new_size)

    @staticmethod
    def sync_buffers_from_agents(agent_list):
        n = len(agent_list)
        for i in range(n):
            Boids.positions[i] = agent_list[i].position
            Boids.directions[i] = agent_list[i].direction
            Boids.speeds[i] = agent_list[i].speed

    @staticmethod
    def update_agent_logic(current_agent, all_agents):
        Boids.adjust_speed(current_agent)
        Boids.adjust_direction(current_agent)

    @staticmethod
    def calc_cohesion(current_agent, positions, distances, cohesion_radius=None):
        if cohesion_radius is None:
            cohesion_radius = simulation_config["cohesion_radius"]

        mask = (distances > 0) & (distances <= cohesion_radius)

        if not np.any(mask):
            return np.zeros(3)

        relevant_positions = positions[mask]
        average_position = np.mean(relevant_positions, axis=0)

        cohesion_vector = average_position - current_agent.position
        norm = np.linalg.norm(cohesion_vector)
        if norm > 0:
            cohesion_vector /= norm

        return cohesion_vector

    @staticmethod
    def calc_alignment(current_agent, directions, distances, alignment_radius=None):
        if alignment_radius is None:
            alignment_radius = simulation_config["alignment_radius"]

        # Exclude self (distance = 0) and apply radius
        mask = (distances > 0) & (distances <= alignment_radius)

        if not np.any(mask):
            return np.zeros(3)

        relevant_directions = directions[mask]
        alignment_vector = np.mean(relevant_directions, axis=0)

        norm = np.linalg.norm(alignment_vector)
        if norm > 0:
            alignment_vector /= norm

        return alignment_vector

    @staticmethod
    def calc_separation(deltas, distances, separation_radius=None):
        if separation_radius is None:
            separation_radius = simulation_config["separation_radius"]

        # Mask: ignore self and keep only agents within radius
        mask = (distances > 0) & (distances <= separation_radius)

        if not np.any(mask):
            return np.zeros(3)

        # Grab relevant slices
        relevant_deltas = deltas[mask]
        relevant_distances = distances[mask].reshape(-1, 1)

        # Inverse-square repulsion
        repulsions = -relevant_deltas / (relevant_distances ** 2)

        separation_vector = np.sum(repulsions, axis=0)

        norm = np.linalg.norm(separation_vector)
        if norm > 0:
            separation_vector /= norm

        return separation_vector

    @staticmethod
    def update_position(current_agent, all_agents):
        Boids.adjust_speed(current_agent)

        velocity = current_agent.direction * current_agent.speed

        # Update position using the new direction, current speed, and time step
        current_agent.position += velocity * 0.1

    @staticmethod
    def adjust_speed(current_agent):
        # Cache simulation_config values
        deceleration = simulation_config["deceleration"]
        acceleration = simulation_config["acceleration"]
        momentum_weight = simulation_config["momentum_weight"]
        max_speed = simulation_config["max_speed"]

        # Compute the desired target speed
        target_speed = Boids.calc_speed(current_agent)

        # If target speed is lower than current speed, decelerate smoothly
        if target_speed < current_agent.speed:
            speed_change = (current_agent.speed - target_speed) * (1 - np.exp(-deceleration))
            current_agent.speed -= speed_change / (1 / momentum_weight)
        else:
            # Normal acceleration logic
            speed_change = (target_speed - current_agent.speed) * (1 - np.exp(-acceleration))
            current_agent.speed += speed_change / (1 / momentum_weight)

        # Clamp speed between min and max
        current_agent.speed = max(current_agent.min_speed, min(max_speed, current_agent.speed))

    @staticmethod
    def calc_speed(current_agent):
        old_direction = Boids.adjust_direction(current_agent)

        turn_sensitivity = simulation_config["turn_sensitivity"]
        max_speed = simulation_config["max_speed"]

        # Compute the angle between current and desired direction
        alignment = np.dot(current_agent.direction, old_direction)
        alignment = np.clip(alignment, -1, 1)
        turn_angle = np.arccos(alignment)


        # Define a small threshold for "going straight" (in radians)
        straight_threshold = np.radians(turn_sensitivity)  # Adjust this as needed

        if turn_angle <= straight_threshold:
            # Going nearly straight: full forward speed.
            return max_speed
        else:
            # Turning: return a negative target speed to trigger deceleration.
            return -abs(max_speed)

    @staticmethod
    def adjust_direction(current_agent):
        direction_alpha = simulation_config["direction_alpha"]
        momentum_weight = simulation_config["momentum_weight"]

        # Normalize vectors to ensure unit length
        current_direction = current_agent.direction / np.linalg.norm(current_agent.direction)
        combined_vector = Boids.calc_direction(current_agent)

        adjusted_alpha = direction_alpha / momentum_weight
        new_direction = (1 - adjusted_alpha) * current_direction + adjusted_alpha * combined_vector

        # Normalize again to maintain unit vector
        new_direction = new_direction / np.linalg.norm(new_direction)
        old_direction = current_agent.direction
        current_agent.direction = new_direction

        return old_direction


    @staticmethod
    def calc_direction(current_agent):
        positions, directions, deltas, distances = Boids.precompute_agent_data(current_agent, Agent.all_agents)

        boundary_threshold = simulation_config["boundary_threshold"]
        boundary_max_force = simulation_config["boundary_max_force"]
        cohesion_weight = simulation_config["cohesion_weight"]
        alignment_weight = simulation_config["alignment_weight"]
        separation_weight = simulation_config["separation_weight"]
        wall_repulsion_weight = simulation_config["wall_repulsion_weight"]

        cohesion_vector = Boids.calc_cohesion(current_agent, positions, distances)
        alignment_vector = Boids.calc_alignment(current_agent, directions, distances)
        separation_vector = Boids.calc_separation(deltas, distances)

        # Calculate wall repulsion force
        wall_repulsion_vector = WallPhysics.calc_wall_repulsion(current_agent)  # Repulsion force from walls

        # Calculate obstacle repulsion force
        obstacle_repulsion_vector = ObstaclePhysics.calculate_obstacle_repulsion(current_agent.position,boundary_threshold,boundary_max_force)

        # Combine vectors with respective weights from simulation configuration
        combined_vector = (
                cohesion_weight * cohesion_vector +
                alignment_weight * alignment_vector +
                separation_weight * separation_vector +
                wall_repulsion_weight * wall_repulsion_vector +
                wall_repulsion_weight * obstacle_repulsion_vector
        )

        # Check if the combined vector is zero or near-zero
        vector_magnitude = np.linalg.norm(combined_vector)
        if vector_magnitude < 1e-6:  # Threshold for near-zero magnitude
            # Replace the zero vector with a random unit vector
            combined_vector = current_agent.direction

        combined_vector = combined_vector / np.linalg.norm(combined_vector)

        return combined_vector

