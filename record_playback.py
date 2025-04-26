import numpy as np
import os
from datetime import datetime

class SimulationRecorder:
    def __init__(self):
        self.recording = False
        self.frames = []
        self.last_reset_frame_index = -1

    def start(self):
        self.recording = True
        self.frames.clear()
        print("[Recorder] Recording started.")

    def record_frame(self, positions, directions, num_agents, boundary_size,
                     obstacle_corner_min, obstacle_corner_max, obstacle_toggle):
        if self.recording:
            self.frames.append({
                'positions': positions.copy(),
                'directions': directions.copy(),
                'num_agents': num_agents,
                'boundary_size': boundary_size,
                'obstacle_corner_min': obstacle_corner_min.copy(),
                'obstacle_corner_max': obstacle_corner_max.copy(),
                'obstacle_toggle': obstacle_toggle,
                'reset': len(self.frames) == self.last_reset_frame_index
            })

    def stop_and_save(self, directory="recordings"):
        if not self.recording or not self.frames:
            print("[Recorder] No recording to save.")
            return

        self.recording = False
        os.makedirs(directory, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(directory, f"swarm_recording_{timestamp}.npz")

        pos_frames = [frame['positions'] for frame in self.frames]
        dir_frames = [frame['directions'] for frame in self.frames]
        num_agents_array = np.array([f['num_agents'] for f in self.frames])
        boundary_array = np.stack([f['boundary_size'] for f in self.frames])
        obstacle_min_array = np.stack([f['obstacle_corner_min'] for f in self.frames])
        obstacle_max_array = np.stack([f['obstacle_corner_max'] for f in self.frames])
        obstacle_toggle = np.array([f['obstacle_toggle'] for f in self.frames])
        reset_flags = np.array([f['reset'] for f in self.frames])

        # Convert to 3D arrays for easy saving: (num_frames, num_agents, 3)
        pos_array = np.stack(pos_frames)
        dir_array = np.stack(dir_frames)

        np.savez_compressed(filename,
                            positions=pos_array,
                            directions=dir_array,
                            num_agents=num_agents_array,
                            boundaries=boundary_array,
                            obstacle_min=obstacle_min_array,
                            obstacle_max=obstacle_max_array,
                            obstacle_toggle=obstacle_toggle,
                            reset_flags = reset_flags,
                            )

        print(f"[Recorder] Recording saved to: {filename}")

    def is_recording(self):
        return self.recording


class SimulationPlayback:
    def __init__(self):
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
        try:
            data = np.load(filepath)
            self.positions = data['positions']  # shape: (T, N, 3)
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
        if self.loaded:
            self.playing = True
            self.current_frame = 0
            print("[Playback] Playback started.")
        else:
            print("[Playback] No recording loaded.")

    def stop(self):
        self.playing = False
        print("[Playback] Playback stopped.")

    def update(self):
        if not self.playing or not self.loaded:
            return None

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

        self.current_frame = (self.current_frame + 1) % self.total_frames  # loop
        return frame_data

    def is_playing(self):
        return self.playing
