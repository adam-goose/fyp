"""
Author: Adam Zelenak
Part of the 3D Swarm Simulation Project
File: simulation.py
Description: Coordinates the overall simulation, including agent spawning, environment setup,
UI binding, and real-time updates. Acts as the primary runtime logic hub for the system.
"""

import csv
import random
import time
import datetime
import psutil

from ursina import *
from agent import Agent
from config import simulation_config

# === SIMULATION PARAMETERS ===

frame_duration = simulation_config["frame_duration"]

# Entity containers
obstacle_entity = None
boundary = None
agent_entities = []
rock_entities = []
lotus_entities = []
pillar_entities = []

color_choices = [
    color.white, color.black, color.red, color.green, color.blue,
    color.yellow, color.orange, color.pink, color.magenta, color.cyan,
    color.azure, color.lime, color.violet, color.brown, color.gray
]

_reset_frame_callback = None

# === RESET CALLBACK REGISTRATION ===

def register_reset_callback(cb):
    """
    Register a callback function to be invoked during boundary resets.

    :param cb: A callable to be registered as the reset callback.
    """
    global _reset_frame_callback
    _reset_frame_callback = cb


# === CAMERA SETUP ===

def set_camera():
    """
    Set the camera position and orientation based on simulation configuration.

    :return: None
    """
    camera.position = simulation_config["camera_position"]
    camera.look_at(simulation_config["camera_look_at"])
    camera.rotation_z = 0  # Prevent camera roll


# === COLOR UTILITY FUNCTION ===

def generate_agent_color(base_color_mode: str, multi_mode: bool = False) -> color:
    """
    Generate a randomized color variation based on a base color name.

    :param base_color_mode: The base color name as a string.
    :param multi_mode: If True, applies a broader hue variation.
    :return: A randomized Ursina color.
    """
    base = getattr(color, base_color_mode, color.cyan if multi_mode else color.white)
    v = clamp(base.v * random.uniform(0.7, 1.8), 0, 1)
    s = clamp(base.s * random.uniform(0.6, 1.3), 0, 1)
    h = base.h + random.uniform(-180, 180) if multi_mode else base.h + random.uniform(-20, 20)
    return color.color(h, s, v)


# === BOUNDARY AND ENVIRONMENT SETUP ===

def create_boundary():
    """
    Create the simulation boundary and decorative elements (rocks, lotus, pillars).

    :return: A list of wall Entity objects.
    """
    x_min, x_max = simulation_config["x_min"], simulation_config["x_max"]
    y_min, y_max = simulation_config["y_min"], simulation_config["y_max"]
    z_min, z_max = simulation_config["z_min"], simulation_config["z_max"]

    floor_boundary_color = Color(120/255, 90/255, 60/255, 1)  # Sandy floor color
    wall_boundary_color = Color(100 / 255, 150 / 255, 255 / 255, 80 / 255)  # Translucent walls

    walls = []

    for side in ('bottom', 'top', 'front', 'back', 'left', 'right'):
        # Define geometry and position for each wall based on side
        if side == 'bottom':
            pos = Vec3((x_min + x_max) / 2, y_min, (z_min + z_max) / 2)
            scale = Vec3(x_max - x_min, z_max - z_min, 1)
            rotation = (90, 0, 0)
            wall = Entity(
                model='quad',
                texture='textures/rock_08_diff_1k.jpg',
                position=pos,
                scale=scale,
                rotation=rotation,
                double_sided=True,
                transparency=False,
            )
        else:
            if side == 'top':
                pos = Vec3((x_min+x_max)/2, y_max, (z_min+z_max)/2)
                scale = Vec3(x_max - x_min, z_max - z_min, 1)
                rotation = (90, 0, 0)
            elif side == 'front':
                pos = Vec3((x_min+x_max)/2, (y_min+y_max)/2, z_min)
                scale = Vec3(x_max - x_min, y_max - y_min, 1)
                rotation = (0, 0, 0)
            elif side == 'back':
                pos = Vec3((x_min+x_max)/2, (y_min+y_max)/2, z_max)
                scale = Vec3(x_max - x_min, y_max - y_min, 1)
                rotation = (0, 180, 0)
            elif side == 'left':
                pos = Vec3(x_min, (y_min+y_max)/2, (z_min+z_max)/2)
                scale = Vec3(z_max - z_min, y_max - y_min, 1)
                rotation = (0, 90, 0)
            elif side == 'right':
                pos = Vec3(x_max, (y_min+y_max)/2, (z_min+z_max)/2)
                scale = Vec3(z_max - z_min, y_max - y_min, 1)
                rotation = (0, -90, 0)

            wall = Entity(
                model='quad',
                color=wall_boundary_color,
                position=pos,
                scale=scale,
                rotation=rotation,
                double_sided=True,
                transparency=True,
            )

        walls.append(wall)

    # Clear any previously created decorations
    for e in rock_entities + lotus_entities + pillar_entities:
        destroy(e)

    rock_entities.clear()
    lotus_entities.clear()
    pillar_entities.clear()

    # Add decorative elements
    create_corners(x_min, x_max, y_min, y_max, z_min, z_max)
    create_rocks(x_min, x_max, y_min, z_min, z_max)
    create_lotus(x_min, x_max, y_max, z_min, z_max)

    return walls

# === ROCK DECORATION ===

def create_rocks(x_min, x_max, y_min, z_min, z_max):
    """
    Create randomized rock decorations distributed throughout the pond area.

    :param x_min: Minimum X boundary.
    :param x_max: Maximum X boundary.
    :param y_min: Floor Y level where rocks sit.
    :param z_min: Minimum Z boundary.
    :param z_max: Maximum Z boundary.
    :return: None
    """
    global rock_entities
    rock_entities.clear()

    width = x_max - x_min
    depth = z_max - z_min
    pond_area = width * depth

    base_rocks = random.randint(30, 50)
    rock_multiplier = pond_area / 100
    num_rocks = int(base_rocks * rock_multiplier)
    num_rocks = clamp(num_rocks, 30, 80)

    buffer = 1  # Ensure rocks don't spawn right at the edges
    num_clusters = random.randint(3, 5)

    # Generate central points for rock clusters
    cluster_centers = [
        Vec3(
            random.uniform(x_min + buffer, x_max - buffer),
            y_min + 0.1,
            random.uniform(z_min + buffer, z_max - buffer)
        )
        for _ in range(num_clusters)
    ]

    rocks_in_clusters = int(num_rocks * 0.8)
    straggler_rocks = num_rocks - rocks_in_clusters

    # Clustered rocks
    for _ in range(rocks_in_clusters):
        cluster = random.choice(cluster_centers)
        pos = Vec3(
            clamp(random.gauss(cluster.x, 1.5), x_min + buffer, x_max - buffer),
            cluster.y,
            clamp(random.gauss(cluster.z, 1.5), z_min + buffer, z_max - buffer)
        )
        spawn_rock(pos)

    # Random standalone rocks
    for _ in range(straggler_rocks):
        pos = Vec3(
            random.uniform(x_min + buffer, x_max - buffer),
            y_min + 0.1,
            random.uniform(z_min + buffer, z_max - buffer)
        )
        spawn_rock(pos)


rock_models = [
    'models/rock1.obj',
    'models/rock2.obj',
    'models/rock3.obj'
]


def spawn_rock(pos):
    """
    Spawn a rock entity at a specific position with randomized scale, color, and rotation.

    :param pos: A Vec3 position for the rock.
    :return: None
    """
    size_factor = random.random()
    if size_factor < 0.75:
        scale = random.uniform(0.005, 0.01)
    elif size_factor < 0.95:
        scale = random.uniform(0.012, 0.02)
    else:
        scale = random.uniform(0.025, 0.04)

    base = Color(50 / 255, 50 / 255, 50 / 255, 1)
    v = clamp(base.v * random.uniform(0.9, 1.1), 0, 1)
    s = clamp(base.s * random.uniform(0.4, 0.9), 0, 1)
    h = base.h + random.uniform(-5, 5)

    # Darker appearance for larger rocks
    if scale > 0.02:
        v *= 0.8
        s *= 0.9

    rock_color = color.color(h, s, v)

    rock = Entity(
        model=random.choice(rock_models),
        color=rock_color,
        position=pos,
        scale=Vec3(
            scale,
            scale * random.uniform(0.5, 1),
            scale
        ),
        rotation=Vec3(
            random.uniform(-5, 5),
            random.uniform(0, 360),
            random.uniform(-5, 5)
        )
    )
    rock_entities.append(rock)


# === LOTUS DECORATION ===

def create_lotus(x_min, x_max, y_max, z_min, z_max):
    """
    Create animated lotus leaf entities that float on the surface.

    :param x_min: Minimum X boundary.
    :param x_max: Maximum X boundary.
    :param y_max: Top Y level (water surface).
    :param z_min: Minimum Z boundary.
    :param z_max: Maximum Z boundary.
    :return: None
    """
    global lotus_entities
    lotus_entities.clear()

    width = x_max - x_min
    depth = z_max - z_min
    pond_area = width * depth

    base_lotus = random.randint(3, 6)
    lotus_multiplier = pond_area / 100
    num_lotus = clamp(int(base_lotus * lotus_multiplier), 3, 10)

    for _ in range(num_lotus):
        scale = random.uniform(50, 80)
        lotus = Entity(
            model='models/lilypad.obj',
            color=Color(60/255, 100/255, 50/255, 1),
            position=Vec3(
                random.uniform(x_min+0.5, x_max-0.5),
                y_max + 0.05,
                random.uniform(z_min+0.5, z_max-0.5)
            ),
            scale=scale,
            rotation=Vec3(0, random.uniform(0, 360), 0)
        )

        # Bobbing animation using time-based sine wave
        lotus.original_y = lotus.y
        lotus.bob_speed = random.uniform(0.5, 1.5)
        lotus.bob_height = random.uniform(0.01, 0.03)

        def bob(self=lotus):
            self.y = self.original_y + math.sin(time.time() * self.bob_speed) * self.bob_height

        lotus.update = bob
        lotus_entities.append(lotus)


# === CORNER STRUCTURE DECORATION ===

def create_corners(x_min, x_max, y_min, y_max, z_min, z_max):
    """
    Create structural corner pillars and connecting beams for visual flair.

    :param x_min: Minimum X boundary.
    :param x_max: Maximum X boundary.
    :param y_min: Bottom Y level.
    :param y_max: Top Y level.
    :param z_min: Minimum Z boundary.
    :param z_max: Maximum Z boundary.
    :return: None
    """
    global pillar_entities
    pillar_entities.clear()

    corners = [
        (x_min, z_min), (x_min, z_max),
        (x_max, z_min), (x_max, z_max)
    ]
    height = y_max - y_min
    pillar_color = color.gray
    beam_color = color.light_gray

    # Vertical corner posts
    for (x, z) in corners:
        pillar = Entity(
            model='cube',
            color=pillar_color,
            position=Vec3(x, y_min + height/2, z),
            scale=Vec3(0.2, height, 0.2)
        )
        pillar_entities.append(pillar)

    # Top beams in Z direction
    for z in [z_min, z_max]:
        beam = Entity(
            model='cube',
            color=beam_color,
            position=Vec3((x_min + x_max)/2, y_max, z),
            scale=Vec3(x_max - x_min + 0.1, 0.05, 0.1)
        )
        pillar_entities.append(beam)

    # Top beams in X direction
    for x in [x_min, x_max]:
        beam = Entity(
            model='cube',
            color=beam_color,
            position=Vec3(x, y_max, (z_min + z_max)/2),
            scale=Vec3(0.1, 0.05, z_max - z_min + 0.1)
        )
        pillar_entities.append(beam)


# === AGENT VISUALS ===

def redraw_agents():
    """
    Destroys and recreates visual representations of all agents,
    using colors based on the selected simulation mode.

    :return: List of Entity objects representing agents.
    """
    global color_choices, agent_entities

    color_mode = simulation_config["agent_colour_mode"]

    # Remove existing agent visuals
    for ent in agent_entities:
        destroy(ent)

    # Assign new randomized color to each agent
    for agent in Agent.all_agents:
        multi = color_mode == "multi"
        agent.color = generate_agent_color(color_mode, multi_mode=multi)

    # Spawn new agent visuals with correct color and position
    agent_entities = [
        Entity(
            model='models/tailor2.obj',
            texture='textures/Tailor_low_DefaultMaterial_BaseColor.png'
                     if simulation_config.get("fish_texture_enabled", True) else None,
            color=agent.color,
            scale=simulation_config["agent_scale"],
            position=agent.position,
            rotation=Vec3(90, -90, 0)  # consistent facing direction
        )
        for agent in Agent.all_agents
    ]

    return agent_entities

# === AGENT INITIALIZATION ===

def spawn_agents():
    """
    Spawn agent objects within the 3D world with randomized positions and directions.

    :return: A list of all Agent instances created.
    """
    Agent.all_agents.clear()

    for _ in range(simulation_config["num_agents"]):
        agent = Agent(
            position=[
                random.uniform(simulation_config["x_min"], simulation_config["x_max"]),
                random.uniform(simulation_config["y_min"], simulation_config["y_max"]),
                random.uniform(simulation_config["z_min"], simulation_config["z_max"])
            ],
            direction=[
                random.uniform(*simulation_config["init_direction_bounds"]),
                random.uniform(*simulation_config["init_direction_bounds"]),
                random.uniform(*simulation_config["init_direction_bounds"])
            ]
        )

    return Agent.all_agents


# === OBSTACLE SETUP ===

def refresh_obstacle():
    """
    Create or replace the obstacle in the simulation environment
    based on the current configuration.

    :return: None
    """
    global obstacle_entity

    # Destroy existing obstacle if present
    if obstacle_entity:
        destroy(obstacle_entity)

    # If obstacle use is disabled in the config, exit early
    if not simulation_config['obstacle_enabled']:
        return

    # Define obstacle placement and size
    min_corner = Vec3(*simulation_config['obstacle_corner_min'])
    max_corner = Vec3(*simulation_config['obstacle_corner_max'])
    center = (min_corner + max_corner) * 0.5
    size = max_corner - min_corner

    # Create a new obstacle entity
    obstacle_entity = Entity(
        model='cube',
        color=simulation_config['obstacle_colour'],
        position=center,
        scale=size,
        collider='box'
    )


# === BOUNDARY RESET ===

def reset_boundaries():
    """
    Reset the boundary walls and decorations based on the current configuration.
    Invokes the reset callback if registered.

    :return: None
    """
    global boundary

    # Trigger external logic if provided
    if _reset_frame_callback:
        _reset_frame_callback()

    # Destroy current boundary entities
    if boundary:
        for wall in boundary:
            destroy(wall)

    # Recreate boundary structure
    boundary = create_boundary()


# === SIMULATION RESET ===

def reset_simulation():
    """
    Reset the simulation: boundaries, obstacle, camera, and agents.

    :return: A list of agent Entity objects.
    """
    global agent_entities

    reset_boundaries()
    refresh_obstacle()
    spawn_agents()
    agent_entities = redraw_agents()
    set_camera()

    return agent_entities


# === PERFORMANCE LOGGING AND AUTO-STAGING ===

frame_data_log = []
frame_counter = 0
last_frame_time = None
agent_stages = [
    (10, 300), (20, 300), (30, 300), (40, 300),
    (50, 300), (60, 300), (70, 300), (80, 300)
]
stage_index = 0
stage_frame_counter = 0
current_agent_count = agent_stages[0][0]

def log_performance():
    """
    Logs frame performance and optionally switches stages after thresholds.

    :return: True if a stage switch occurred, False otherwise.
    """
    global frame_counter, last_frame_time, stage_index, stage_frame_counter, current_agent_count

    now = time.perf_counter()
    frame_time = 0.0
    if last_frame_time is not None:
        frame_time = (now - last_frame_time) * 1000
    last_frame_time = now

    cpu = psutil.cpu_percent(interval=None)
    systime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    num_agents = simulation_config["num_agents"]

    frame_data_log.append([
        systime, frame_counter, stage_index, frame_time, cpu, num_agents
    ])

    frame_counter += 1
    stage_frame_counter += 1

    # Handle auto stage switching
    if stage_index >= len(agent_stages):
        return False

    if stage_frame_counter >= agent_stages[stage_index][1]:
        stage_index += 1
        stage_frame_counter = 0

        if stage_index < len(agent_stages):
            next_count = agent_stages[stage_index][0]
            simulation_config["num_agents"] = next_count
            reset_simulation()
            print(f"\n>>> Switching to {next_count} agents (Stage {stage_index})\n")
            return True
        else:
            print(">>> All stages complete.")
            with open("frame_log.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "frame", "stage", "frame_time_ms", "cpu_percent", "num_agents"])
                writer.writerows(frame_data_log)

            print("[Simulation] Frame log saved to frame_log.csv.")

    return False
