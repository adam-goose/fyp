###
# Deprecated - NO LONGER USED FOR TESTING
###

import pytest
import numpy as np
from movement_model import Boids
from physics import *
from agent import Agent

# Mock the Agent class for testing
class MockAgent:
    all_agents = []  # Global list of all agents

    def __init__(self, position):
        self.position = np.array(position)
        MockAgent.all_agents.append(self)

    @classmethod
    def reset_agents(cls):
        cls.all_agents = []

def test_get_neighbours_within_radius():
    """
    Test that the method correctly identifies neighbours within the perception radius.
    Includes cases where some agents are inside the radius, and others are outside.
    """
    # Arrange: Create agents in the simulation
    MockAgent.reset_agents()  # Clear any existing agents
    agent1 = MockAgent([0, 0, 0])  # Test agent
    agent2 = MockAgent([5, 0, 0])  # Within radius
    agent3 = MockAgent([12, 0, 0])  # Outside radius
    agent4 = MockAgent([7, 7, 0])  # Diagonally within radius

    # Act: Call the method on agent1
    neighbours = Boids.get_neighbours_within_radius(agent1, MockAgent.all_agents, perception_radius=10.0)

    # Assert: Verify only valid neighbours are included
    assert len(neighbours) == 2, f"Expected 1 neighbor, found {len(neighbours)}"
    assert neighbours[0] == agent2, f"Incorrect neighbor found: {neighbours[0].position if neighbours else None}"

def test_no_neighbours():
    """
    Test that no neighbors are returned when all agents are outside the perception radius.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent
    agent2 = MockAgent([15, 0, 0])  # Outside radius
    agent3 = MockAgent([20, 20, 0])  # Far outside radius

    # Act
    neighbors = Boids.get_neighbours_within_radius(agent1, MockAgent.all_agents, perception_radius=10.0)

    # Assert
    assert len(neighbors) == 0, f"Expected no neighbors, found {len(neighbors)}"

def test_edge_of_radius():
    """
    Test that an agent exactly at the edge of the perception radius is included as a neighbor.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent
    agent2 = MockAgent([10, 0, 0])  # Exactly at the edge of the radius

    # Act
    neighbors = Boids.get_neighbours_within_radius(agent1, MockAgent.all_agents, perception_radius=10.0)

    # Assert
    assert len(neighbors) == 1, f"Expected 1 neighbor, found {len(neighbors)}"
    assert neighbors[0] == agent2, f"Expected agent2 to be the neighbor, found {neighbors[0].position if neighbors else None}"

def test_self_exclusion():
    """
    Test that an agent does not include itself as a neighbor.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent

    # Act
    neighbors = Boids.get_neighbours_within_radius(agent1, MockAgent.all_agents, perception_radius=10.0)

    # Assert
    assert len(neighbors) == 0, f"Expected no neighbors, found {len(neighbors)}"

def test_cohesion_no_neighbors():
    """
    Test that cohesion returns a zero vector when there are no neighbors.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent

    # Act
    cohesion_vector = Boids.calc_cohesion([], agent1, cohesion_radius=5.0)

    # Assert
    assert np.all(cohesion_vector == np.array([0, 0, 0])), f"Expected zero vector, got {cohesion_vector}"


def test_cohesion_single_neighbor():
    """
    Test that cohesion returns a vector pointing directly toward the single neighbor.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent
    neighbor = MockAgent([5, 0, 0])  # Single neighbor

    # Act
    cohesion_vector = Boids.calc_cohesion([neighbor], agent1, cohesion_radius=5.0)

    # Assert
    expected_vector = np.array([1, 0, 0])  # Direction to the neighbor
    assert np.allclose(cohesion_vector, expected_vector), f"Expected {expected_vector}, got {cohesion_vector}"


def test_cohesion_multiple_neighbors():
    """
    Test that cohesion calculates a vector pointing toward the average centre of neighbour agents.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent
    neighbor1 = MockAgent([5, 0, 0])
    neighbor2 = MockAgent([0, 5, 0])

    # Act
    cohesion_vector = Boids.calc_cohesion([neighbor1, neighbor2], agent1, cohesion_radius=5.0)

    # Assert
    expected_com = np.array([0.70710678, 0.70710678, 0])  # Normalised average of [5, 0, 0] and [0, 5, 0]
    expected_vector = expected_com - agent1.position
    assert np.allclose(cohesion_vector, expected_vector), f"Expected {expected_vector}, got {cohesion_vector}"


def test_cohesion_overlapping_neighbors():
    """
    Test that cohesion handles overlapping neighbors correctly.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent
    neighbor1 = MockAgent([0, 3, 2])
    neighbor2 = MockAgent([0, 3, 2])  # Overlapping neighbor

    # Act
    cohesion_vector = Boids.calc_cohesion([neighbor1, neighbor2], agent1, cohesion_radius=5.0)

    # Assert
    expected_vector = np.array([0, 0.83205029, 0.55470020]) - agent1.position
    assert np.allclose(cohesion_vector, expected_vector), f"Expected {expected_vector}, got {cohesion_vector}"

def test_alignment_no_neighbors():
    """
    Test that alignment returns a zero vector when there are no neighbors.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent

    # Act
    alignment_vector = Boids.calc_alignment([], agent1, alignment_radius=4.0)

    # Assert
    assert np.all(alignment_vector == np.array([0, 0, 0])), f"Expected zero vector, got {alignment_vector}"


def test_alignment_single_neighbor():
    """
    Test that alignment aligns with the single neighbour's direction.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent
    neighbour = MockAgent([2, 2, 0])  # Single neighbour
    neighbour.direction = np.array([1, 0, 0])  # Neighbor's direction

    # Act
    alignment_vector = Boids.calc_alignment([neighbour], agent1, alignment_radius=4.0)

    # Assert
    expected_vector = neighbour.direction / np.linalg.norm(neighbour.direction)  # Normalized direction
    assert np.allclose(alignment_vector, expected_vector), f"Expected {expected_vector}, got {alignment_vector}"


def test_alignment_multiple_neighbors():
    """
    Test that alignment calculates the average direction of multiple neighbors.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent
    neighbor1 = MockAgent([2, 2, 0])
    neighbor1.direction = np.array([1, 0, 0])  # Neighbor 1 direction
    neighbor2 = MockAgent([4, 0, 0])
    neighbor2.direction = np.array([0, 1, 0])  # Neighbor 2 direction

    # Act
    alignment_vector = Boids.calc_alignment([neighbor1, neighbor2], agent1, alignment_radius=4.0)

    # Assert
    average_direction = np.mean([neighbor1.direction, neighbor2.direction], axis=0)
    expected_vector = average_direction / np.linalg.norm(average_direction)  # Normalized average direction
    assert np.allclose(alignment_vector, expected_vector), f"Expected {expected_vector}, got {alignment_vector}"


def test_alignment_with_radius():
    """
    Test that alignment considers only neighbors within the alignment radius.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent
    neighbor1 = MockAgent([2, 2, 0])
    neighbor1.direction = np.array([1, 0, 0])  # Neighbor 1 direction
    neighbor2 = MockAgent([15, 0, 0])  # Outside radius
    neighbor2.direction = np.array([0, 1, 0])  # Neighbor 2 direction

    # Act
    alignment_vector = Boids.calc_alignment([neighbor1, neighbor2], agent1, alignment_radius=4.0)

    # Assert
    expected_vector = neighbor1.direction / np.linalg.norm(neighbor1.direction)  # Normalized direction of neighbor1
    assert np.allclose(alignment_vector, expected_vector), f"Expected {expected_vector}, got {alignment_vector}"

def test_separation_no_neighbors():
    """
    Test that separation returns a zero vector when there are no neighbors.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent

    # Act
    separation_vector = Boids.calc_separation([], agent1, separation_radius=10.0)

    # Assert
    assert np.all(separation_vector == np.array([0, 0, 0])), f"Expected zero vector, got {separation_vector}"


def test_separation_single_neighbor():
    """
    Test that separation calculates the correct repulsion vector from a single neighbor.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent
    neighbor = MockAgent([3, 3, 0])  # Single neighbor

    # Act
    separation_vector = Boids.calc_separation([neighbor], agent1, separation_radius=10.0)

    # Assert
    expected_vector = np.array([0, 0, 0], dtype=float) - np.array([3, 3, 0], dtype=float)  # Repulsion vector
    expected_vector /= np.linalg.norm(expected_vector)  # Normalize
    assert np.allclose(separation_vector, expected_vector), f"Expected {expected_vector}, got {separation_vector}"


def test_separation_multiple_neighbors():
    """
    Test that separation combines repulsion vectors from multiple neighbors.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent
    neighbor1 = MockAgent([3, 0, 0])  # Neighbor 1
    neighbor2 = MockAgent([0, 3, 0])  # Neighbor 2

    # Act
    separation_vector = Boids.calc_separation([neighbor1, neighbor2], agent1, separation_radius=10.0)

    # Assert
    # Repulsion vectors
    vector1 = np.array([0, 0, 0], dtype=float) - np.array([3, 0, 0], dtype=float)
    vector2 = np.array([0, 0, 0], dtype=float) - np.array([0, 3, 0], dtype=float)
    combined_vector = vector1 + vector2
    expected_vector = combined_vector / np.linalg.norm(combined_vector)  # Normalize
    assert np.allclose(separation_vector, expected_vector), f"Expected {expected_vector}, got {separation_vector}"


def test_separation_overlapping_neighbors():
    """
    Test that separation handles overlapping neighbors gracefully.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent
    neighbor1 = MockAgent([0, 0, 0])  # Overlapping neighbor
    neighbor2 = MockAgent([0, 0, 0])  # Another overlapping neighbor

    # Act
    separation_vector = Boids.calc_separation([neighbor1, neighbor2], agent1, separation_radius=10.0)

    # Assert
    assert np.all(separation_vector == np.array([0, 0, 0])), f"Expected zero vector, got {separation_vector}"

def test_separation_closer_neighbor_dominates():
    """
    Test that the separation vector is influenced more by the closer neighbor.
    """
    # Arrange
    MockAgent.reset_agents()
    agent1 = MockAgent([0, 0, 0])  # Test agent
    closer_neighbor = MockAgent([2, 0.1, 0])  # Closer neighbor
    farther_neighbor = MockAgent([-5, 0.1, 0])  # Farther neighbor

    # Act
    separation_vector = Boids.calc_separation([closer_neighbor, farther_neighbor], agent1, separation_radius=10.0)

    # Assert
    # Closer neighbor's repulsion dominates, so the vector should align closer to [-1, 0, 0]
    closer_repulsion = (agent1.position - closer_neighbor.position) / np.linalg.norm(agent1.position - closer_neighbor.position)**2
    farther_repulsion = (agent1.position - farther_neighbor.position) / np.linalg.norm(agent1.position - farther_neighbor.position)**2
    combined_repulsion = closer_repulsion + farther_repulsion
    expected_direction = combined_repulsion / np.linalg.norm(combined_repulsion)  # Normalize

    assert np.allclose(separation_vector, expected_direction), f"Expected {expected_direction}, got {separation_vector}"

def test_adjust_speed_high_alignment():
    """
    Test that speed increases towards desired_speed for high alignment.
    """
    # Arrange
    mock_agent = MockAgent(position=[0, 0, 0])  # Initialize position (if required, depends on MockAgent)
    mock_agent.direction = np.array([1, 0, 0])  # Aligns with combined_vector
    mock_agent.speed = 5.0
    mock_agent.desired_speed = 10.0
    mock_agent.min_speed = 2.0
    mock_agent.max_speed = 12.0
    combined_vector = np.array([1, 0, 0])  # Perfect alignment

    # Act
    Boids.adjust_speed(combined_vector, mock_agent)

    # Assert
    assert mock_agent.speed > 5.0, f"Speed did not increase as expected: {mock_agent.speed}"
    assert mock_agent.speed <= mock_agent.desired_speed, "Speed exceeded desired speed"

def test_adjust_speed_low_alignment():
    """
    Test that speed decreases for low alignment.
    """
    # Arrange
    mock_agent = MockAgent(position=[0, 0, 0])
    mock_agent.direction = np.array([1, 0, 0])  # Misaligned with combined_vector
    mock_agent.speed = 8.0
    mock_agent.desired_speed = 10.0
    mock_agent.min_speed = 2.0
    mock_agent.max_speed = 12.0
    combined_vector = np.array([0, 1, 0])  # Perpendicular to direction

    # Act
    Boids.adjust_speed(combined_vector, mock_agent)

    # Assert
    assert mock_agent.speed < 8.0, f"Speed did not decrease as expected: {mock_agent.speed}"
    assert mock_agent.speed >= mock_agent.min_speed, "Speed went below minimum speed"

def test_adjust_speed_clamped_speed():
    """
    Test that speed is clamped to min_speed and max_speed.
    """
    # Arrange
    mock_agent = MockAgent(position=[0, 0, 0])
    mock_agent.direction = np.array([1, 0, 0])
    mock_agent.speed = 5.0
    mock_agent.desired_speed = 20.0  # Desired exceeds max_speed
    mock_agent.min_speed = 4.9  # Min speed very close to current speed
    mock_agent.max_speed = 5.1  # Max speed very close to current speed
    combined_vector = np.array([1, 0, 0])  # Perfect alignment

    # Act
    Boids.adjust_speed(combined_vector, mock_agent)

    # Assert
    assert mock_agent.speed <= mock_agent.max_speed, "Speed exceeded max_speed"
    assert mock_agent.speed >= mock_agent.min_speed, "Speed went below min_speed"

def test_calc_movement_no_neighbors():
    """
    Test that calc_movement works correctly when there are no neighbors.
    """
    # Arrange
    mock_agent = MockAgent(position=[0, 0, 0])  # Agent at origin
    mock_agent.direction = np.array([1, 0, 0])  # Moving along X-axis
    mock_agent.speed = 5.0
    mock_agent.desired_speed = 5.0
    mock_agent.min_speed = 2.0
    mock_agent.max_speed = 10.0
    mock_agent.neighbors = []  # No neighbors in the environment

    # Act
    boids_model = Boids()
    movement_vector = boids_model.calc_movement(mock_agent, MockAgent.all_agents)

    # Assert
    expected_vector = mock_agent.direction  # No neighbors, movement should remain the same
    assert np.allclose(movement_vector, expected_vector), f"Expected {expected_vector}, got {movement_vector}"


def test_calc_movement_with_neighbors():
    """
    Test calc_movement with neighbors influencing cohesion, alignment, and separation.
    """
    # Arrange
    MockAgent.reset_agents()
    mock_agent = MockAgent(position=[0, 0, 0])
    mock_agent.direction = np.array([1, 0, 0])
    mock_agent.speed = 5.0
    mock_agent.desired_speed = 5.0
    mock_agent.min_speed = 2.0
    mock_agent.max_speed = 10.0

    # Add neighbors
    neighbor1 = MockAgent(position=[5, 5, 0])  # Diagonal
    neighbor2 = MockAgent(position=[-5, -5, 0])  # Opposite diagonal
    neighbor1.direction = np.array([1, 1, 0])
    neighbor2.direction = np.array([-1, -1, 0])

    # Act
    boids_model = Boids()
    movement_vector = boids_model.calc_movement(mock_agent, MockAgent.all_agents)

    # Assert
    assert np.linalg.norm(movement_vector) > 0, "Movement vector magnitude should not be zero"
    assert np.allclose(movement_vector, movement_vector / np.linalg.norm(movement_vector)), \
        f"Expected normalized vector, got {movement_vector}"


def test_calc_movement_wall_repulsion():
    """
    Test calc_movement considering wall repulsion.
    """
    # Arrange
    mock_agent = MockAgent(position=[1, 1, 1])  # Close to a hypothetical wall at (0, 0, 0)
    mock_agent.direction = np.array([1, 0, 0])  # Initially moving along the X-axis
    mock_agent.speed = 5.0
    mock_agent.desired_speed = 5.0
    mock_agent.min_speed = 2.0
    mock_agent.max_speed = 10.0

    # Mock wall repulsion (requires WallPhysics.calc_wall_repulsion to be mocked if it's not implemented)
    def mock_wall_repulsion(agent):
        return np.array([-0.5, -0.5, -0.5])  # Gradual push away from the origin

    WallPhysics.calc_wall_repulsion = mock_wall_repulsion  # Replace method for testing

    # Act
    boids_model = Boids()
    movement_vector = boids_model.calc_movement(mock_agent, MockAgent.all_agents)

    # Assert
    assert np.linalg.norm(movement_vector) > 0, "Movement vector should not be zero"

    # The movement vector should have a component influenced by wall repulsion
    wall_vector = mock_wall_repulsion(mock_agent)
    dot_product = np.dot(movement_vector, wall_vector)
    assert dot_product < 0, f"Expected movement influenced by wall repulsion, got {movement_vector}"

