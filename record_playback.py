import numpy as np
import os
from datetime import datetime


class SimulationRecorder:
    def __init__(self):
        """
        Initialize the recorder.
        """
        self.recording = False
        self.frames = []
        self.last_reset_frame_index = -1

    def start(self):
        """
        Begin recording simulation frames.
        """
        self.recording = True
        self.frames.clear()
        print("[Recorder] Recording started.")

    def record_frame(self, positions, directions, num_agents, boundary_size,
                     obstacle_corner_min, obstacle_corner_max, obstacle_toggle):
        """
        Capture and store a snapshot of the current simulation frame.

        :param positions: List of agent position vectors.
        :param directions: List of agent direction vectors.
        :param num_agents: Number of agents in the frame.
        :param boundary_size: 3D size of the simulation boundary.
        :param obstacle_corner_min: Min corner of the obstacle.
        :param obstacle_corner_max: Max corner of the obstacle.
        :param obstacle_toggle: Boolean whether obstacle is enabled.
        :return: None
        """
        if self.recording:
            self.frames.append({
                'positions': positions.copy(),
                'directions': directions.copy(),
                'num_agents': num_agents,
                'boundary_size': boundary_size,
                'obstacle_corner_min': obstacle_corner_min.copy(),
                'obstacle_corner_max': obstacle_corner_max.copy(),
                'obstacle_toggle': obstacle_toggle,
                'reset': len(self.frames) == self.last_reset_frame_index  # track if this was a reset frame
            })

    def stop_and_save(self, directory="recordings"):
        """
        Stop recording and save the data to a compressed .npz file.

        :param directory: Folder where recordings should be stored.
        :return: None
        """
        if not self.recording or not self.frames:
            print("[Recorder] No recording to save.")
            return

        self.recording = False
        os.makedirs(directory, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(directory, f"swarm_recording_{timestamp}.npz")

        # Convert lists of per-frame data into arrays
        pos_frames = [frame['positions'] for frame in self.frames]
        dir_frames = [frame['directions'] for frame in self.frames]
        num_agents_array = np.array([f['num_agents'] for f in self.frames])
        boundary_array = np.stack([f['boundary_size'] for f in self.frames])
        obstacle_min_array = np.stack([f['obstacle_corner_min'] for f in self.frames])
        obstacle_max_array = np.stack([f['obstacle_corner_max'] for f in self.frames])
        obstacle_toggle = np.array([f['obstacle_toggle'] for f in self.frames])
        reset_flags = np.array([f['reset'] for f in self.frames])

        # Create 3D numpy arrays: (num_frames, num_agents, 3)
        pos_array = np.stack(pos_frames)
        dir_array = np.stack(dir_frames)

        # Save all data to compressed file
        np.savez_compressed(filename,
                            positions=pos_array,
                            directions=dir_array,
                            num_agents=num_agents_array,
                            boundaries=boundary_array,
                            obstacle_min=obstacle_min_array,
                            obstacle_max=obstacle_max_array,
                            obstacle_toggle=obstacle_toggle,
                            reset_flags=reset_flags)

        print(f"[Recorder] Recording saved to: {filename}")

    def is_recording(self):
        """
        Check if recording is currently active.

        :return: True if recording, False otherwise.
        """
        return self.recording


class SimulationPlayback:
    def __init__(self):
        """
        Initialize the playback system.
        """
        self.positions = None
        self.directions = None
        self.num_agents = None
        self.boundaries = None
        self.obstacle_min = None
        self.obstacle_max = None
        self.obstacle_toggle = None
        self.total_frames = 0
        self.current_frame = 0
        self.loaded = False
        self.playing = False
        self.reset_flags = None

    def load(self, filepath):
        """
        Load recorded simulation data from an .npz file.

        :param filepath: Path to the saved recording file.
        :return: None
        """
        try:
            data = np.load(filepath)
            self.positions = data['positions']
            self.directions = data['directions']
            self.num_agents = data['num_agents']
            self.boundaries = data['boundaries']
            self.obstacle_min = data['obstacle_min']
            self.obstacle_max = data['obstacle_max']
            self.obstacle_toggle = data['obstacle_toggle']
            self.reset_flags = data['reset_flags']

            self.total_frames = self.positions.shape[0]
            self.current_frame = 0
            self.loaded = True
            print(f"[Playback] Loaded {self.total_frames} frames from {filepath}")
        except Exception as e:
            print(f"[Playback] Failed to load recording: {e}")
            self.loaded = False

    def start(self):
        """
        Start playback from the beginning.

        :return: None
        """
        if self.loaded:
            self.playing = True
            self.current_frame = 0
            print("[Playback] Playback started.")
        else:
            print("[Playback] No recording loaded.")

    def stop(self):
        """
        Stop playback.

        :return: None
        """
        self.playing = False
        print("[Playback] Playback stopped.")

    def update(self):
        """
        Advance playback and return the current frame's simulation data.

        :return: A dictionary of simulation state for the current frame.
        """
        if not self.playing or not self.loaded:
            return None

        # Retrieve data from current frame
        frame_data = {
            'positions': self.positions[self.current_frame],
            'directions': self.directions[self.current_frame],
            'num_agents': self.num_agents[self.current_frame],
            'boundary_size': self.boundaries[self.current_frame],
            'obstacle_corner_min': self.obstacle_min[self.current_frame],
            'obstacle_corner_max': self.obstacle_max[self.current_frame],
            'obstacle_toggle': self.obstacle_toggle[self.current_frame],
            'reset': self.reset_flags[self.current_frame]
        }

        # Advance frame (loop back if at end)
        self.current_frame = (self.current_frame + 1) % self.total_frames
        return frame_data

    def is_playing(self):
        """
        Check if playback is currently active.

        :return: True if playing, False otherwise.
        """
        return self.playing