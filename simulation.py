import random
from ursina import *
from agent import Agent
from config import simulation_config

# Frame timing setup
frame_duration = simulation_config["frame_duration"]

obstacle_entity = None
agent_entities = []
color_choices = [
        color.white, color.black,
        color.red, color.green, color.blue,
        color.yellow, color.orange, color.pink,
        color.magenta, color.cyan, color.azure,
        color.lime, color.violet, color.brown,
        color.gray
    ]

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

    edges = [
        (2, 3), (2, 6), (6, 7), (3, 7),  # Bottom Square
        (4, 5), (0, 1), (0, 4), (1, 5),  # Top Square
        (0, 2), (7, 5), (4, 6), (3, 1),  # Front & Back Cross
        (4, 3), (7, 0), (5, 2), (1, 6),  # Left & Right Cross
        (0, 3), (4, 7), (6, 5), (1, 2),  # Verticals
        (4, 1), (5, 0), (7, 2), (3, 6)   # Top & Bottom Cross
    ]

    # Create and return the Entity for the boundary
    return Entity(
        model=Mesh(vertices=vertices, triangles=edges, mode='line'), # Use the wireframe mode
        color=color.white33 # Set the wireframe colour to white
    )

def refresh_obstacle():
    global obstacle_entity

    if obstacle_entity:
        destroy(obstacle_entity)

    if not simulation_config['obstacle_enabled']:
        return

    min_corner = Vec3(*simulation_config['obstacle_corner_min'])
    max_corner = Vec3(*simulation_config['obstacle_corner_max'])

    center = (min_corner + max_corner) * 0.5
    size = max_corner - min_corner

    obstacle_entity = Entity(
        model='cube',
        color=simulation_config['obstacle_colour'],
        position=center,
        scale=size,
        collider='box'
    )

boundary = create_boundary()
def reset_boundaries():
    global boundary

    # Destroy current boundary
    if boundary:
        destroy(boundary)

    # Recreate boundary using current config
    boundary = create_boundary()


def spawn_agents():
    print(f"SPAWNING AGENTS ------")
    Agent.all_agents.clear()

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

    return Agent.all_agents

from ursina import Mesh

def create_arrowhead_mesh():
    vertices = [
        (0.0,  0.0,  1.0),   # tip
        (-0.2, -0.2, 0.0),   # base 1
        ( 0.2, -0.2, 0.0),   # base 2
        ( 0.2,  0.2, 0.0),   # base 3
        (-0.2,  0.2, 0.0)    # base 4
    ]
    faces = [
        (0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1),  # front
        (2, 1, 0), (3, 2, 0), (4, 3, 0), (1, 4, 0)   # backfaces
    ]
    return Mesh(vertices=vertices, triangles=faces, mode='triangle')


def redraw_agents():
    global color_choices, agent_entities

    color_mode = simulation_config["agent_colour_mode"]

    for ent in agent_entities:
        destroy(ent)

    for agent in Agent.all_agents:
        if color_mode == "multi":
            base = getattr(color, color_mode, color.cyan)
            v = clamp(base.v * random.uniform(0.7, 1.8), 0, 1)
            s = clamp(base.s * random.uniform(0.6, 1.3), 0, 1)
            h = base.h + random.uniform(-180, 180)

            agent.color = color.color(h, s, v)
        else:
            base = getattr(color, color_mode, color.white)
            v = clamp(base.v * random.uniform(0.7, 1.8), 0, 1)
            s = clamp(base.s * random.uniform(0.6, 1.3), 0, 1)
            h = base.h + random.uniform(-40, 40)

            agent.color = color.color(h, s, v)

    agent_entities = [
        Entity(
            model='models/tailor.obj',
            color=agent.color,  # ← use the color set in spawn_agents
            scale=simulation_config["agent_scale"],
            position=agent.position
        )
        for agent in Agent.all_agents
    ]

    return agent_entities

def reset_simulation(recorder = None):
    global agent_entities, boundary


    if recorder and recorder.is_recording():
        recorder.last_reset_frame_index = len(recorder.frames)

    # Destroy the current boundary
    destroy(boundary)
    refresh_obstacle()

    color_mode = simulation_config["agent_colour_mode"]

    # Recreate agents and their visual entities
    spawn_agents()
    agent_entities = redraw_agents()

    # Recreate boundary and camera
    boundary = create_boundary()
    set_camera()

    return agent_entities

