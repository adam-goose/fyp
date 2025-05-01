from ursina import *
app = Ursina()

import simulation
from simulation import *
from config import *
from settings_ui import *
from config import default_simulation_config, simulation_config, pack_boundaries, unpack_boundaries
import time
import psutil
from collections import deque
import csv
import atexit
import numpy as np
import datetime
from movement_model import Boids
from record_playback import SimulationRecorder, SimulationPlayback
import tkinter as tk
from tkinter import filedialog

# Hide the main Tkinter window
tk_root = tk.Tk()
tk_root.withdraw()

DirectionalLight(shadows=True, rotation=(90, 10, 0))
AmbientLight(color=Color(255/255, 245/255, 220/255, 100/255))  # Warm white

last_time = time.time()

recorder = SimulationRecorder()
playback = SimulationPlayback()

# Initialize agents
agent_entities = simulation.reset_simulation()

auto_rotate_enabled = False
orbit_angle = 0

current_count = 0

# 🔁 Frame tracking + logging
frame_data_log = []
frame_counter = 0
last_frame_time = None

# 🎯 Agent stage management
agent_stages = [(10, 300), (20, 300), (30, 300), (40, 300), (50, 300), (60, 300), (70, 300), (80, 300)]
stage_index = 0
stage_frame_counter = 0
current_agent_count = agent_stages[0][0]  # start with 20


simulation.set_camera()

def log_performance(current_agents):
    global frame_counter, last_frame_time, frame_data_log, agent_stages, stage_index, stage_frame_counter, current_agent_count

    now = time.perf_counter()
    frame_time = 0.0
    if last_frame_time is not None:
        frame_time = (now - last_frame_time) * 1000  # ms
    last_frame_time = now

    cpu = psutil.cpu_percent(interval=None)
    systime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # millisecond precision

    num_agents = simulation_config["num_agents"]


    frame_data_log.append([
        systime,
        frame_counter,                # 0 - global frame count
        stage_index,                  # 1 - current stage
        frame_time,                   # 2 - frame time
        cpu,                          # 3 - CPU usage
        num_agents                   # 4 - number of agents
    ])

    frame_counter += 1
    stage_frame_counter += 1

    # Move to the next stage after 300 frames
    if stage_frame_counter >= agent_stages[stage_index][1]:
        stage_index += 1
        stage_frame_counter = 0

        if stage_index < len(agent_stages):
            next_agent_count = agent_stages[stage_index][0]
            simulation_config["num_agents"] = next_agent_count
            reset_simulation()
            print(f"\n>>> Switching to {next_agent_count} agents (Stage {stage_index})\n")
        else:
            print(">>> All stages complete.")

def save_full_log(filename="full_performance_log.csv"):
    with open(filename, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Time", "Frame", "Stage", "Frame Time (ms)", "CPU Usage (%)",
            "Agent Count"
        ])
        writer.writerows(frame_data_log)


#atexit.register(save_full_log)

def update():
    global last_time
    global orbit_angle, current_count, agent_entities
    current_time = time.time()
    elapsed_time = current_time - last_time

    if auto_rotate_enabled:
        orbit_angle += simulation_config["camera_orbit_speed"] * time.dt

        cam_x = orbit_radius * math.cos(orbit_angle)
        cam_z = orbit_radius * math.sin(orbit_angle)
        cam_y = orbit_height  # direct from user config at toggle time

        camera.position = Vec3(cam_x, cam_y, cam_z)
    else:
        camera.position = simulation_config["camera_position"]

    camera.look_at(simulation_config["camera_look_at"])
    camera.rotation_z = 0  # Force no roll


    if elapsed_time < frame_duration:
        time.sleep(frame_duration - elapsed_time)  # Sleep to maintain 30 FPS


    if recorder.is_recording():
        packed_boundaries = pack_boundaries(simulation_config)
        recorder.record_frame(Boids.positions, Boids.directions, simulation_config["num_agents"], packed_boundaries,
                              simulation_config["obstacle_corner_min"], simulation_config["obstacle_corner_max"],
                              simulation_config["obstacle_enabled"])

    if not playback.is_playing():
        # Normal simulation logic
        for agent, agent_entity in zip(Agent.all_agents, agent_entities):
            agent.update_position()
            agent_entity.position = agent.position
            agent_entity.look_at(agent.direction + agent.position)

    else:
        # Playback logic
        frame = playback.update()
        if frame:
            pos_frame = frame['positions']
            dir_frame = frame['directions']

            if frame['reset'] or playback.current_frame == 1:
                print(f"RESET FRAME ----------------------------------------------- RESET FRAME")
                current_count = frame['num_agents']
                simulation_config["num_agents"] = current_count
                agent_entities = reset_simulation()

            # Update config and environment visuals
            simulation_config["obstacle_enabled"] = frame['obstacle_toggle']
            simulation_config["obstacle_corner_min"] = frame['obstacle_corner_min']
            simulation_config["obstacle_corner_max"] = frame['obstacle_corner_max']
            unpack_boundaries(frame['boundary_size'], simulation_config)
            refresh_obstacle()
            reset_boundaries()

            # Update agent visuals
            for i in range(current_count):
                Agent.all_agents[i].position = pos_frame[i]
                Agent.all_agents[i].direction = dir_frame[i]
                agent_entities[i].position = pos_frame[i]
                agent_entities[i].look_at(Agent.all_agents[i].direction + Agent.all_agents[i].position)
                agent_entities[i].rotate(Vec3(90, -90, 0))

    last_time = time.time()
    #log_performance(Agent.all_agents)


def toggle_auto_rotate():
    global auto_rotate_enabled, orbit_angle, orbit_radius, orbit_height

    auto_rotate_enabled = not auto_rotate_enabled

    if auto_rotate_enabled:
        orbit_angle = 0

        # Use the user's configured camera position
        pos = simulation_config["camera_position"]
        orbit_radius = math.sqrt(pos[0] ** 2 + pos[2] ** 2)
        orbit_height = pos[1]

        if orbit_radius < 0.01:
            orbit_radius = 10  # fallback if they're dead center

def reset_helper():
    global agent_entities
    agent_entities = simulation.reset_simulation(recorder)

def handle_agent_redraw():
    global agent_entities
    agent_entities = redraw_agents()

register_redraw_callback(handle_agent_redraw)

def reset_simulation_to_default():
    # Overwrite current config with defaults
    for key, value in default_simulation_config.items():
        simulation_config[key] = value

    # Optionally: update slider values to reflect reset (if you want the UI to reflect it visually)
    # Update slider visuals to reflect default values
    for container in settings_containers:
        for child in container.children:
            if isinstance(child, Slider) and hasattr(child, 'key'):
                if '[' in child.key and ']' in child.key:
                    base_key, index = child.key.split('[')
                    index = int(index[:-1])  # strip the closing bracket
                    child.value = default_simulation_config[base_key][index]
                else:
                    child.value = default_simulation_config[child.key]

    # Reset sim with the fresh config
    reset_helper()

def toggle_recording():
    if not recorder.is_recording():
        recorder.start()
        record_toggle.text = 'Stop & Save'
    else:
        recorder.stop_and_save()
        record_toggle.text = 'Start Recording'

def toggle_playback():
    if not playback.is_playing():
        filepath = filedialog.askopenfilename(
            title="Select a recording file",
            filetypes=[("NumPy compressed", "*.npz")]
        )
        if filepath:
            playback.load(filepath)
            playback.start()
            playback_toggle.text = 'Stop Playback'
    else:
        playback.stop()
        playback_toggle.text = 'Play Recording'

# Window
window.size = (1280, 720)
window.borderless = False

# DEBUGGING - GIVES AN AVERAGE SPEED READOUT AND SPECIFIC SPEEDS FOR FIRST 3 AGENTS
#speed_readout = Text(text="Avg Speed: 0.0", position=(-0.7, 0.4), scale=2, color=color.white)
#first_agent_speed_readout = Text(text="First Agent Speed: 0.0", position=(-0.7, 0.3), scale=2, color=color.white)
#second_agent_speed_readout = Text(text="Second Agent Speed: 0.0", position=(-0.7, 0.2), scale=2, color=color.white)
#third_agent_speed_readout = Text(text="Third Agent Speed: 0.0", position=(-0.7, 0.1), scale=2, color=color.white)

# Create the settings UI and get the containers.
ui_elements = create_settings_ui()
background_dimmer = ui_elements['background_dimmer']
physics_ui = ui_elements['physics_ui']
simulation_ui = ui_elements['simulation_ui']
agents_ui = ui_elements['agents_ui']
movement_ui = ui_elements['movement_ui']
settings_containers = ui_elements['settings_containers']
camera_ui = ui_elements['camera_ui']
obstacle_ui = ui_elements['obstacle_ui']

# Create buttons to toggle each settings UI.
physics_button = Button(text="Physics", parent=camera.ui,
                        position=(-0.7, 0.4), scale=(0.2, 0.05))
physics_button.on_click = lambda: toggle_settings(physics_ui, background_dimmer, settings_containers)

simulation_button = Button(text="Simulation", parent=camera.ui,
                           position=(-0.7, 0.3), scale=(0.2, 0.05))
simulation_button.on_click = lambda: toggle_settings(simulation_ui, background_dimmer, settings_containers)

agent_button = Button(text="Agent", parent=camera.ui,
                      position=(-0.7, 0.2), scale=(0.2, 0.05))
agent_button.on_click = lambda: toggle_settings(agents_ui, background_dimmer, settings_containers)

movement_button = Button(text="Movement", parent=camera.ui,
                      position=(-0.7, 0.1), scale=(0.2, 0.05))
movement_button.on_click = lambda: toggle_settings(movement_ui, background_dimmer, settings_containers)

camera_button = Button(text="Camera", parent=camera.ui,
                       position=(-0.7, -0.0), scale=(0.2, 0.05))
camera_button.on_click = lambda: toggle_settings(camera_ui, background_dimmer, settings_containers)

obstacle_button = Button(text="Obstacle", parent=camera.ui,
                       position=(-0.7, -0.1), scale=(0.2, 0.05))
obstacle_button.on_click = lambda: toggle_settings(obstacle_ui, background_dimmer, settings_containers)

reset_button = Button(text="Reset Sim", parent=camera.ui,
                      position=(-0.7, -0.2, -0.5), scale=(0.2, 0.05), color=color.azure)
reset_button.on_click = reset_helper

reset_default_button = Button(text="Reset Default", parent=camera.ui,
                              position=(-0.7, -0.3, -0.5), scale=(0.2, 0.05), color=color.orange)
reset_default_button.on_click = reset_simulation_to_default

orbit_toggle = Button(text="Auto Orbit: Off", parent=camera_ui,
                      position=(-0.15, -0.00), scale=(0.4, 0.05), color=color.blue)
orbit_toggle.on_click = lambda: (
    toggle_auto_rotate(),
    setattr(orbit_toggle, 'text', f"Auto Orbit: {'On' if auto_rotate_enabled else 'Off'}")
)

reset_bounds_button = Button(
    text="Reset Boundaries", parent=simulation_ui,
    position=(-0.15, -0.10), scale=(0.4, 0.05), color=color.blue
)
reset_bounds_button.on_click = reset_boundaries

record_toggle = Button(
    text='Start Recording',
    parent=camera.ui,
    position=(-0.7, -0.4, -0.5),  # one step below Reset Default
    scale=(0.2, 0.05),
    color=color.red
)
record_toggle.on_click = toggle_recording

playback_toggle = Button(
    text='Play Recording',
    parent=camera.ui,
    position=(-0.7, -0.5, -0.5),  # below record toggle
    scale=(0.2, 0.05),
    color=color.green
)
playback_toggle.on_click = toggle_playback

# Run the Ursina app
app.run()