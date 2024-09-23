import subprocess, json, os
from video import Video
from audio import Audio
from time import sleep

class Media(object):
    """Represents an MP4 or MKV media file.
    Note: This class only supports MP4 and MKV files, other formats may work but are not guaranteed to work.
    """
    def __init__(self, path):
        self._path = path
        self._metadata = self._get_metadata()

        self._video_streams = []
        self._audio_streams = []

        self._duration = float(self._metadata['format']['duration'])
        self._size = int(self._metadata['format']['size'])

        for stream in self._metadata['streams']:
            if stream['codec_type'] == 'video':
                index = stream['index']
                duration = float(stream['duration'])
                bitrate = int(stream['bit_rate'])
                width = int(stream['width'])
                height = int(stream['height'])
                fps = float(stream['r_frame_rate'].split('/')[0]) / float(stream['r_frame_rate'].split('/')[1])
                self._video_streams.append(Video(index, duration, bitrate, width, height, fps))
            elif stream['codec_type'] == 'audio':
                index = stream['index']
                duration = float(stream['duration'])
                bitrate = int(stream['bit_rate'])
                self._audio_streams.append(Audio(index, duration, bitrate))
    
    ## Properties
    def get_path(self):
        return self._path
    
    def get_metadata(self):
        return self._metadata
    
    def get_duration(self):
        return self._duration
    
    def get_size(self):
        return self._size

    def get_video_streams(self):
        return self._video_streams
    
    def get_audio_streams(self):
        return self._audio_streams
    
    path = property(get_path)
    metadata = property(get_metadata)
    duration = property(get_duration)
    size = property(get_size)
    video_streams = property(get_video_streams)
    audio_streams = property(get_audio_streams)

    ## Private methods
    def _get_metadata(self):
        """Returns a dictionary of metadata from ffprobe."""
        command = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', self._path]
        output = json.loads(subprocess.check_output(command))
        return output

    ## Public methods
    

if __name__ == "__main__":
    me_file = Media('Replay 2023-12-25 22-31-45.mp4')
    print(me_file.metadata)
    print(me_file.duration)
    print(me_file.size)
    