from ursina import *
app = Ursina()
window.render_mode = 'forward'

# --- Imports ---
import simulation
from simulation import *
from config import *
from settings_ui import *
from config import default_simulation_config, simulation_config, pack_boundaries, unpack_boundaries
import time
import psutil
import csv
import datetime
from movement_model import Boids
from record_playback import SimulationRecorder, SimulationPlayback
import tkinter as tk
from tkinter import filedialog
import math

# --- Tkinter setup for file dialogs ---
tk_root = tk.Tk()
tk_root.withdraw()

# --- Scene Lighting ---
DirectionalLight(shadows=True, rotation=(90, 20, 0))
AmbientLight(color=Color(255/255, 245/255, 220/255, 100/255))  # Soft warm ambient light

# --- Runtime State ---
last_time = time.time()
recorder = SimulationRecorder()
playback = SimulationPlayback()
agent_entities = simulation.reset_simulation()

# Orbit camera state
auto_rotate_enabled = False
orbit_angle = 0

# Register callback to mark reset points in the recorder
simulation.register_reset_callback(lambda: setattr(recorder, 'last_reset_frame_index', len(recorder.frames)))


# === UPDATE LOOP ===
def update():
    """
    Core update loop for the simulation.
    Handles camera rotation, simulation step, frame recording, and playback.
    """
    global last_time, orbit_angle, current_count, agent_entities
    current_time = time.time()
    elapsed_time = current_time - last_time

    # --- Camera Position Update ---
    update_camera_position()

    # --- Frame Throttling ---
    if elapsed_time < frame_duration:
        time.sleep(frame_duration - elapsed_time)

    # --- Frame Recording ---
    if recorder.is_recording():
        packed_boundaries = pack_boundaries(simulation_config)
        recorder.record_frame(
            Boids.positions,
            Boids.directions,
            simulation_config["num_agents"],
            packed_boundaries,
            simulation_config["obstacle_corner_min"],
            simulation_config["obstacle_corner_max"],
            simulation_config["obstacle_enabled"]
        )

    # --- Simulation or Playback Step ---
    if not playback.is_playing():
        # Normal simulation update step
        for agent, agent_entity in zip(Agent.all_agents, agent_entities):
            agent.update_position()
            update_agent_entities(agent, agent_entity)
    else:
        # Apply a saved frame from recording
        frame = playback.update()
        if frame:
            apply_playback_frame(frame)

    last_time = time.time()


# === CAMERA LOGIC ===
def toggle_auto_rotate():
    """Toggle camera orbiting and initialize orbital parameters."""
    global auto_rotate_enabled, orbit_angle, orbit_radius, orbit_height
    auto_rotate_enabled = not auto_rotate_enabled

    if auto_rotate_enabled:
        orbit_angle = 0
        pos = simulation_config["camera_position"]
        orbit_radius = math.sqrt(pos[0] ** 2 + pos[2] ** 2)
        orbit_height = pos[1]
        if orbit_radius < 0.01:
            orbit_radius = 10


def rotate_camera():
    """Move the camera in a horizontal circular orbit around the scene."""
    global orbit_angle
    orbit_angle += simulation_config["camera_orbit_speed"] * time.dt

    cam_x = orbit_radius * math.cos(orbit_angle)
    cam_z = orbit_radius * math.sin(orbit_angle)
    cam_y = orbit_height
    camera.position = Vec3(cam_x, cam_y, cam_z)


def update_camera_position():
    """Update the camera's position and look direction based on orbit toggle."""
    if auto_rotate_enabled:
        rotate_camera()
    else:
        camera.position = simulation_config["camera_position"]

    camera.look_at(simulation_config["camera_look_at"])
    camera.rotation_z = 0


# === RESET LOGIC ===
def reset_helper(to_default=False):
    """Reset the simulation. Optionally resets all config to default values."""
    if to_default:
        reset_simulation_to_default(settings_containers)

    global agent_entities
    agent_entities = simulation.reset_simulation()


# === PLAYBACK FRAME HANDLING ===
def apply_playback_frame(frame):
    """
    Apply a playback frame to update simulation visuals and parameters.
    """
    global current_count, agent_entities

    pos_frame = frame['positions']
    dir_frame = frame['directions']

    if frame['reset'] or playback.current_frame == 1:
        # Reset and respawn agents from the frame's state
        current_count = frame['num_agents']
        simulation_config['num_agents'] = current_count
        unpack_boundaries(frame['boundary_size'], simulation_config)
        agent_entities = reset_simulation()

    # Apply obstacle parameters
    simulation_config['obstacle_enabled'] = frame['obstacle_toggle']
    simulation_config['obstacle_corner_min'] = frame['obstacle_corner_min']
    simulation_config['obstacle_corner_max'] = frame['obstacle_corner_max']
    refresh_obstacle()

    # Update visual position and orientation
    for i in range(current_count):
        agent = Agent.all_agents[i]
        agent.position = pos_frame[i]
        agent.direction = dir_frame[i]
        update_agent_entities(agent, agent_entities[i])


def update_agent_entities(agent, entity):
    """Apply agent state to the corresponding entity in the scene."""
    entity.position = agent.position
    entity.look_at(agent.direction + agent.position)


# === TOGGLE CONTROLS ===
def toggle_recording():
    """Start or stop the recorder depending on its state."""
    if playback.is_playing():
        print("⚠️ Cannot start recording while playback is active.")
        return
    if not recorder.is_recording():
        recorder.start()
        record_toggle.text = 'Stop & Save'
    else:
        recorder.stop_and_save()
        record_toggle.text = 'Start Recording'


def toggle_playback():
    """Start or stop playback from a file."""
    if recorder.is_recording():
        print("⚠️ Cannot start playback while recording is active.")
        return
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


# === CALLBACK HOOK ===
def handle_agent_redraw():
    """Trigger full visual redraw of all agents."""
    global agent_entities
    agent_entities = redraw_agents()

register_redraw_callback(handle_agent_redraw)


# === UI INITIALIZATION ===
window.size = (1280, 720)
window.borderless = False

ui_elements = create_settings_ui()
background_dimmer = ui_elements['background_dimmer']
physics_ui = ui_elements['physics_ui']
simulation_ui = ui_elements['simulation_ui']
agents_ui = ui_elements['agents_ui']
movement_ui = ui_elements['movement_ui']
settings_containers = ui_elements['settings_containers']
camera_ui = ui_elements['camera_ui']
obstacle_ui = ui_elements['obstacle_ui']

# Left-side button panel (category toggles)
build_button_panel(settings_containers, background_dimmer, ui_elements)

# Control buttons (record, playback, reset)
record_toggle, playback_toggle = build_control_buttons(
    reset_helper,
    lambda: reset_helper(to_default=True),
    toggle_recording,
    toggle_playback
)

# Camera orbit toggle
build_orbit_toggle(camera_ui, toggle_auto_rotate)

# Start simulation
app.run()
