import random
from ursina import *
from agent import Agent
from config import simulation_config

# Frame timing setup
frame_duration = simulation_config["frame_duration"]

# Define camera position and direction
def set_camera():
    """
    Define camera position and direction according to values set by simulation_config.

    """
    camera.position = simulation_config["camera_position"]  # Position of the camera within the scene
    camera.look_at(simulation_config["camera_look_at"])  # Direction the camera looks at
    camera.rotation_z = 0  # Force no roll


def create_boundary():
    """
    Create a 3D boundary box using the boundary values from simulation_config.

    Returns:
        Entity: A boundary box as an Entity with a wireframe model.
    """
    vertices = [
        # Define the vertices of the boundary box
        Vec3(simulation_config["x_min"], simulation_config["y_min"], simulation_config["z_min"]),   # Bottom-front-left
        Vec3(simulation_config["x_max"], simulation_config["y_min"], simulation_config["z_min"]),   # Bottom-front-right
        Vec3(simulation_config["x_max"], simulation_config["y_max"], simulation_config["z_min"]),   # Top-front-right
        Vec3(simulation_config["x_min"], simulation_config["y_max"], simulation_config["z_min"]),   # Top-front-left
        Vec3(simulation_config["x_min"], simulation_config["y_min"], simulation_config["z_max"]),   # Bottom-back-left
        Vec3(simulation_config["x_max"], simulation_config["y_min"], simulation_config["z_max"]),   # Bottom-back-right
        Vec3(simulation_config["x_max"], simulation_config["y_max"], simulation_config["z_max"]),   # Top-back-left
        Vec3(simulation_config["x_min"], simulation_config["y_max"], simulation_config["z_max"])    # Top-back-right
    ]

    triangles = [
        # This is super confusing and I don't know how I got it to look right
        (0, 1, 2), (0, 2, 3),  # Bottom face
        (4, 5, 6), (4, 6, 7),  # Top face
        (0, 1, 5), (0, 5, 4),  # Front face
        (3, 1, 4),             # Front face diagonal
        (1, 2, 6), (1, 6, 5),  # Right face
        (2, 3, 7), (2, 7, 6),  # Back face
        (7, 5, 6),             # Back face diagonal
        (3, 0, 4), (3, 4, 7)   # Left face
    ]

    # Create and return the Entity for the boundary
    return Entity(
        model=Mesh(vertices=vertices, triangles=triangles, mode='line'), # Use the wireframe mode
        color=color.white # Set the wireframe colour to white
    )


def spawn_agents():
    """
    Spawn agents according to values set by simulation_config.

    Returns: List of agents with set position and direction.
    """
    print(f"SPAWNING AGENTS ------")

    color_mode = simulation_config["agent_colour_mode"]
    color_choices = [
        color.white, color.black,
        color.red, color.green, color.blue,
        color.yellow, color.orange, color.pink,
        color.magenta, color.cyan, color.azure,
        color.lime, color.violet, color.brown,
        color.gray
    ]

    agents = []

    for _ in range(simulation_config["num_agents"]):
        agent = Agent(
            position=[
                random.uniform(*simulation_config["init_position_bounds"]),
                random.uniform(*simulation_config["init_position_bounds"]),
                random.uniform(*simulation_config["init_position_bounds"])
            ],
            direction=[
                random.uniform(*simulation_config["init_direction_bounds"]),
                random.uniform(*simulation_config["init_direction_bounds"]),
                random.uniform(*simulation_config["init_direction_bounds"])
            ]
        )

        # Assign color
        if color_mode == "multi":
            agent.color = random.choice(color_choices)
        else:
            agent.color = getattr(color, color_mode, color.white)

        agents.append(agent)

    return agents


