from obswebsocket import obsws, requests, events
from media import Media
import os, subprocess
from time import sleep

class OBS(obsws):
    def __init__(self, host, port, password):
        super().__init__(host, port, password)
        self.register(self._get_last_replay_buffer_replay, events.ReplayBufferSaved)
        self._attempt_connect()

        self._last_replay_filename = None
        self._last_recording_filename = None

    ## Private methods
    def _get_last_replay_buffer_replay(self, message):
        """Returns the path of the last replay buffer replay."""
        self._last_replay_filename = message.getSavedReplayPath()
    
    def _attempt_connect(self):
        """Attempts to connect to OBS."""
        attemps = 0
        while attemps < 10:
            try:
                self.connect()
                return
            except ConnectionRefusedError:
                attempts += 1

        raise ConnectionRefusedError("Could not connect to OBS.")
    
    def _remux_replay(self, file_extension: str):
        # get the file name without the extension and add the new extension
        file_base_name = os.path.splitext(self._last_replay_filename)[0]
        new_file_name = file_base_name + "." + file_extension

        # remux the file WITH FFMPEG to ensure metadata gets converted properly
        remux_command = ['ffmpeg', '-y', '-i', self._last_replay_filename, '-c', 'copy', '-map', '0', new_file_name]
        p = subprocess.Popen(remux_command)
        p.wait()

        # rename class attribute to the new file name
        self._last_replay_filename = new_file_name

    def _remux_recording(self, file_extension: str):
        # get the file name without the extension and add the new extension
        file_base_name = os.path.splitext(self._last_recording_filename)[0]
        new_file_name = file_base_name + "." + file_extension

        # remux the file WITH FFMPEG to ensure metadata gets converted properly
        remux_command = ['ffmpeg', '-y', '-i', self._last_recording_filename, '-c', 'copy', '-map', '0', new_file_name]
        p = subprocess.Popen(remux_command)
        p.wait()

        # rename class attribute to the new file name
        self._last_recording_filename = new_file_name

    def _file_in_use(self, file_path: str) -> bool:
        """Returns True if the file is in use, otherwise returns False."""
        try:
            os.rename(file_path, file_path)
            return False
        except OSError:
            return True

    ## Public methods
    
    def start_recording(self):
        """Starts recording."""
        self.call(requests.StartRecord())
        
    def stop_recording(self):
        """Stops recording and returns the Media object of the recording."""
        self._last_recording_filename = self.call(requests.StopRecord()).getOutputPath()
        
        while self._file_in_use(self._last_recording_filename):
            pass

        self._remux_recording("mp4")
        return Media(self._last_recording_filename)

    def pause_recording(self):
        """Pauses recording."""
        self.call(requests.PauseRecord())

    def resume_recording(self):
        """Resumes recording."""
        self.call(requests.ResumeRecord())

    def start_replay_buffer(self):
        """Starts the replay buffer."""
        self.call(requests.StartReplayBuffer())

    def stop_replay_buffer(self):
        """Stops the replay buffer"""
        self.call(requests.StopReplayBuffer())

    def save_replay_buffer(self):
        """Saves the replay buffer to disk and returns the Media object of the saved file."""
        old_replay_filename = self._last_replay_filename
        self.call(requests.SaveReplayBuffer())
        
        while self._last_replay_filename == old_replay_filename:
            sleep(0.1)

        # since media objects only support MP4 files, remux the replay to MP4
        self._remux_replay("mp4")

        return Media(self._last_replay_filename)
    

if __name__ == "__main__":
    from config_reader import config

    c = config("config.env")
    o = OBS(c.get_obs_ip(), c.get_obs_port(), c.get_obs_password())
    o.save_replay_buffer()
