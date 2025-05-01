import random
from ursina import *
from agent import Agent
from config import simulation_config

# Frame timing setup
frame_duration = simulation_config["frame_duration"]

obstacle_entity = None
agent_entities = []
rock_entities = []
lotus_entities = []
pillar_entities = []
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


from ursina import *

from ursina import *
import random

def create_boundary():
    x_min, x_max = simulation_config["x_min"], simulation_config["x_max"]
    y_min, y_max = simulation_config["y_min"], simulation_config["y_max"]
    z_min, z_max = simulation_config["z_min"], simulation_config["z_max"]

    floor_boundary_color = Color(120/255, 90/255, 60/255, 1)  # Sandy
    wall_boundary_color = Color(100 / 255, 150 / 255, 255 / 255, 80 / 255)  # Soft translucent blue

    walls = []

    # Create water walls
    for side in ('bottom', 'top', 'front', 'back', 'left', 'right'):
        if side == 'bottom':
            pos = Vec3((x_min + x_max) / 2, y_min, (z_min + z_max) / 2)
            width = x_max - x_min
            depth = z_max - z_min
            scale = Vec3(width, depth, 1)
            rotation = (90, 0, 0)

            wall = Entity(
                model='quad',
                texture='textures/rock_face_diff_2k.jpg',
                position=pos,
                scale=scale,
                rotation=rotation,
                double_sided=True,
                transparency=False,
            )

        elif side == 'top':
            pos = Vec3((x_min+x_max)/2, y_max, (z_min+z_max)/2)
            scale = Vec3(x_max-x_min, z_max-z_min, 1)
            rotation = (90, 0, 0)
        elif side == 'front':
            pos = Vec3((x_min+x_max)/2, (y_min+y_max)/2, z_min)
            scale = Vec3(x_max-x_min, y_max-y_min, 1)
            rotation = (0, 0, 0)
        elif side == 'back':
            pos = Vec3((x_min+x_max)/2, (y_min+y_max)/2, z_max)
            scale = Vec3(x_max-x_min, y_max-y_min, 1)
            rotation = (0, 180, 0)
        elif side == 'left':
            pos = Vec3(x_min, (y_min+y_max)/2, (z_min+z_max)/2)
            scale = Vec3(z_max-z_min, y_max-y_min, 1)
            rotation = (0, 90, 0)
        elif side == 'right':
            pos = Vec3(x_max, (y_min+y_max)/2, (z_min+z_max)/2)
            scale = Vec3(z_max-z_min, y_max-y_min, 1)
            rotation = (0, -90, 0)

        if side != 'bottom':
            wall = Entity(
                model='quad',
                color=boundary_color,
                position=pos,
                scale=scale,
                rotation=rotation,
                double_sided=True,
                transparency=True,
            )
        boundary_color = wall_boundary_color
        walls.append(wall)

    for e in rock_entities + lotus_entities + pillar_entities:
        destroy(e)

    rock_entities.clear()
    lotus_entities.clear()
    pillar_entities.clear()
    
    # Create decorative elements
    print(f"CREATE BOUNDARY")
    create_corners(x_min, x_max, y_min, y_max, z_min, z_max)
    create_rocks(x_min, x_max, y_min, z_min, z_max)
    create_lotus(x_min, x_max, y_max, z_min, z_max)

    return walls


def create_rocks(x_min, x_max, y_min, z_min, z_max):
    global rock_entities
    rock_entities.clear()

    width = x_max - x_min
    depth = z_max - z_min
    pond_area = width * depth

    base_rocks = random.randint(30, 50)
    rock_multiplier = pond_area / 100
    num_rocks = int(base_rocks * rock_multiplier)
    num_rocks = clamp(num_rocks, 30, 80)

    buffer = 1  # How far from walls rocks are allowed
    num_clusters = random.randint(3, 5)

    # Select cluster centers, not too close to walls
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

    # --- Clustered Rocks ---
    for _ in range(rocks_in_clusters):
        cluster = random.choice(cluster_centers)
        pos = Vec3(
            clamp(random.gauss(cluster.x, 1.5), x_min + buffer, x_max - buffer),
            cluster.y,
            clamp(random.gauss(cluster.z, 1.5), z_min + buffer, z_max - buffer)
        )
        spawn_rock(pos)

    # --- Straggler Rocks ---
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

    # For larger rocks, darken even more
    if scale > 0.02:
        v *= 0.8  # darker
        s *= 0.9  # slightly desaturate

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
            random.uniform(0, 360),  # rotation around X (flat spin)                       # no Y spin
            random.uniform(-5, 5)                       # no Z roll
        )
    )
    rock_entities.append(rock)





# 🌸 Lotus leaves floating at top
def create_lotus(x_min, x_max, y_max, z_min, z_max):
    global lotus_entities
    lotus_entities.clear()

    width = x_max - x_min
    depth = z_max - z_min
    pond_area = width * depth

    base_lotus = random.randint(3, 6)
    lotus_multiplier = pond_area / 100
    num_lotus = int(base_lotus * lotus_multiplier)
    num_lotus = clamp(num_lotus, 3, 10)

    for _ in range(num_lotus):
        scale = random.uniform(50, 80)
        lotus = Entity(
            model='models/lilypad.glb',
            color=color.green,
            position=Vec3(
                random.uniform(x_min+0.5, x_max-0.5),
                y_max + 0.05,
                random.uniform(z_min+0.5, z_max-0.5)
            ),
            scale=scale,
            rotation=Vec3(
                0,
                random.uniform(0, 360),
                0
            )
        )

        lotus.original_y = lotus.y
        lotus.bob_speed = random.uniform(0.5, 1.5)
        lotus.bob_height = random.uniform(0.01, 0.03)

        def bob(self=lotus):
            self.y = self.original_y + math.sin(time.time() * self.bob_speed) * self.bob_height

        lotus.update = bob

        lotus_entities.append(lotus)


# 🧱 Corner pillars
def create_corners(x_min, x_max, y_min, y_max, z_min, z_max):
    global pillar_entities
    pillar_entities.clear()

    corners = [
        (x_min, z_min),
        (x_min, z_max),
        (x_max, z_min),
        (x_max, z_max)
    ]
    height = y_max - y_min

    pillar_color = color.gray
    beam_color = color.light_gray

    for (x, z) in corners:
        pillar = Entity(
            model='cube',
            color=pillar_color,
            position=Vec3(x, y_min + height/2, z),
            scale=Vec3(0.2, height, 0.2)
        )
        pillar_entities.append(pillar)

    for z in [z_min, z_max]:
        beam = Entity(
            model='cube',
            color=beam_color,
            position=Vec3((x_min + x_max)/2, y_max, z),
            scale=Vec3(x_max - x_min + 0.1, 0.05, 0.1)
        )
        pillar_entities.append(beam)

    for x in [x_min, x_max]:
        beam = Entity(
            model='cube',
            color=beam_color,
            position=Vec3(x, y_max, (z_min + z_max)/2),
            scale=Vec3(0.1, 0.05, z_max - z_min + 0.1)
        )
        pillar_entities.append(beam)


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
        for wall in boundary:
            destroy(wall)

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
            model='models/tailor3.glb',
            #color=agent.color,  # ← use the color set in spawn_agents
            scale=simulation_config["agent_scale"],
            position=agent.position,
            rotation=Vec3(90, -90, 0)
        )
        for agent in Agent.all_agents
    ]

    return agent_entities

def reset_simulation(recorder = None):
    global agent_entities, boundary


    if recorder and recorder.is_recording():
        recorder.last_reset_frame_index = len(recorder.frames)

    # Destroy the current boundary
    reset_boundaries()
    refresh_obstacle()

    color_mode = simulation_config["agent_colour_mode"]

    # Recreate agents and their visual entities
    spawn_agents()
    agent_entities = redraw_agents()

    # Recreate camera
    set_camera()

    return agent_entities

