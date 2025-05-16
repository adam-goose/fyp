"""
Author: Adam Zelenak
Part of the 3D Swarm Simulation Project
File: movement_model.py
Description: Contains the core Boids-based movement logic: cohesion, separation, and alignment.
"""

from config import simulation_config
from agent import Agent
from physics import *
import numpy as np

class MovementModel:
    """
    Abstract base class for movement models.

    Subclasses must implement:
        - update_position(current_agent, all_agents): defines how an agent updates its position.
    """
    def update_position(self, current_agent, all_agents):
        """
        Update the position of an agent. Must be implemented by subclasses.

        :param current_agent: The agent whose position is being updated.
        :param all_agents: A list of all agents in the simulation.
        """
        raise NotImplementedError("Subclasses must implement update_position")


class Boids(MovementModel):
    """
    Boids movement model implementing flocking behavior with cohesion, alignment,
    separation, and environmental repulsion forces.
    """
    # Preallocated buffers for efficient neighbour calculations
    buffer_size = 100
    positions = np.zeros((buffer_size, 3))
    directions = np.zeros((buffer_size, 3))
    deltas = np.zeros((buffer_size, 3))
    distances = np.zeros(buffer_size)
    speeds = np.zeros(buffer_size)

    @staticmethod
    def precompute_agent_data(current_agent, all_agents):
        """
        Precompute relative positions, directions, and distances to all agents.
        This optimises subsequent cohesion, alignment, and separation calculations.
        """
        n = len(all_agents)
        if n > Boids.buffer_size:
            Boids.resize_buffers(n)

        # Store global data relative to current agent
        Boids.positions[:n] = [a.position for a in all_agents]
        Boids.directions[:n] = [a.direction for a in all_agents]
        Boids.speeds[:n] = [a.speed for a in all_agents]
        Boids.deltas[:n] = Boids.positions[:n] - current_agent.position
        Boids.distances[:n] = np.linalg.norm(Boids.deltas[:n], axis=1)

        return Boids.positions[:n], Boids.directions[:n], Boids.deltas[:n], Boids.distances[:n]

    @staticmethod
    def resize_buffers(new_size):
        """
        Resize internal numpy buffers to accommodate more agents.
        """
        Boids.buffer_size = new_size
        Boids.positions = np.zeros((new_size, 3))
        Boids.directions = np.zeros((new_size, 3))
        Boids.deltas = np.zeros((new_size, 3))
        Boids.distances = np.zeros(new_size)

    @staticmethod
    def sync_buffers_from_agents(agent_list):
        """
        Sync position, direction, and speed buffers from the agent list.
        This may be used when rendering or debugging.
        """
        n = len(agent_list)
        for i in range(n):
            Boids.positions[i] = agent_list[i].position
            Boids.directions[i] = agent_list[i].direction
            Boids.speeds[i] = agent_list[i].speed

    @staticmethod
    def update_agent_logic(current_agent, all_agents):
        """
        Apply both steering and speed update logic to an agent.
        This is useful in simulations with separate movement and update steps.
        """
        Boids.adjust_speed(current_agent)
        Boids.adjust_direction(current_agent)

    def update_position(self, current_agent, all_agents):
        """
        Update an agent's position using its speed and direction.
        The actual movement step based on calculated state.
        """
        self.adjust_speed(current_agent)
        velocity = current_agent.direction * current_agent.speed
        current_agent.position += velocity * 0.1  # Movement step

    @staticmethod
    # Cohesion pulls agents toward the average position of neighbors within a radius
    # This encourages the group to stay together
    def calc_cohesion(current_agent, positions, distances, cohesion_radius=None):
        """
        Compute cohesion vector toward nearby agents.
        Steers the agent toward the average position of neighbors.
        """
        cohesion_radius = cohesion_radius or simulation_config["cohesion_radius"]
        mask = (distances > 0) & (distances <= cohesion_radius)
        if not np.any(mask): return np.zeros(3)
        average_position = np.mean(positions[mask], axis=0)
        vec = average_position - current_agent.position
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else np.zeros(3)

    @staticmethod
    # Alignment steers an agent in the same direction as its neighbors
    # It uses the average heading of agents within the alignment radius
    def calc_alignment(current_agent, directions, distances, alignment_radius=None):
        """
        Compute alignment vector from neighboring agents' headings.
        Steers agent to align with average heading of neighbors.
        """
        alignment_radius = alignment_radius or simulation_config["alignment_radius"]
        mask = (distances > 0) & (distances <= alignment_radius)
        if not np.any(mask): return np.zeros(3)
        avg = np.mean(directions[mask], axis=0)
        norm = np.linalg.norm(avg)
        return avg / norm if norm > 0 else np.zeros(3)

    @staticmethod
    # Separation pushes agents away from others that are too close
    # Inverse square repulsion is used for stronger force at closer distances
    def calc_separation(deltas, distances, separation_radius=None):
        """
        Compute separation vector to avoid crowding.
        Repels from neighbors that are too close.
        """
        separation_radius = separation_radius or simulation_config["separation_radius"]
        mask = (distances > 0) & (distances <= separation_radius)
        if not np.any(mask): return np.zeros(3)
        repulsions = -deltas[mask] / (distances[mask].reshape(-1, 1) ** 2)
        vec = np.sum(repulsions, axis=0)
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else np.zeros(3)

    @staticmethod
    def adjust_speed(current_agent):
        """
        Smoothly adjust the speed of the agent based on turning and target dynamics.
        Uses exponential smoothing to simulate acceleration and deceleration.
        """
        acc = simulation_config["acceleration"]
        dec = simulation_config["deceleration"]
        weight = simulation_config["momentum_weight"]
        max_spd = simulation_config["max_speed"]
        target = Boids.calc_speed(current_agent)

        if target < current_agent.speed:
            # Decelerating
            delta = (current_agent.speed - target) * (1 - np.exp(-dec))
            current_agent.speed -= delta / (1 / weight)
        else:
            # Accelerating
            delta = (target - current_agent.speed) * (1 - np.exp(-acc))
            current_agent.speed += delta / (1 / weight)

        # Clamp to valid speed range
        current_agent.speed = max(current_agent.min_speed, min(max_spd, current_agent.speed))

    @staticmethod
    def calc_speed(current_agent):
        """
        Determine target speed based on turning angle.
        If turning sharply, speed is reduced. If moving straight, speed is maximised.
        """
        old = Boids.adjust_direction(current_agent)
        align = np.clip(np.dot(current_agent.direction, old), -1, 1)
        angle = np.arccos(align)
        threshold = np.radians(simulation_config["turn_sensitivity"])
        return simulation_config["max_speed"] if angle <= threshold else -abs(simulation_config["max_speed"])

    @staticmethod
    # Adjust direction with momentum blending
    # Smooths out sudden direction changes using a weighted average
    def adjust_direction(current_agent):
        """
        Blend current direction with calculated desired direction vector.
        Used for momentum-based steering.
        """
        alpha = simulation_config["direction_alpha"] / simulation_config["momentum_weight"]
        current = current_agent.direction / np.linalg.norm(current_agent.direction)
        target = Boids.calc_direction(current_agent)
        new = (1 - alpha) * current + alpha * target
        new /= np.linalg.norm(new)
        old = current_agent.direction
        current_agent.direction = new
        return old

    @staticmethod
    # Calculate the desired movement direction based on multiple forces
    # Combines cohesion, alignment, separation, and environmental repulsion
    def calc_direction(current_agent):
        """
        Combine all weighted steering vectors to compute final heading.
        Includes wall and obstacle avoidance.
        """
        pos, dir, delta, dist = Boids.precompute_agent_data(current_agent, Agent.all_agents)
        cfg = simulation_config

        # Weighted sum of all steering behaviours
        combined = (
            cfg["cohesion_weight"] * Boids.calc_cohesion(current_agent, pos, dist) +
            cfg["alignment_weight"] * Boids.calc_alignment(current_agent, dir, dist) +
            cfg["separation_weight"] * Boids.calc_separation(delta, dist) +
            cfg["wall_repulsion_weight"] * WallPhysics.calc_wall_repulsion(current_agent) +
            cfg["wall_repulsion_weight"] * ObstaclePhysics.calculate_obstacle_repulsion(current_agent.position, cfg["boundary_threshold"], cfg["boundary_max_force"])
        )

        # Normalize result, fall back to current direction if zero
        norm = np.linalg.norm(combined)
        return (combined / norm) if norm > 1e-6 else current_agent.direction
