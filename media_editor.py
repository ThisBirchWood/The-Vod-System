from media import Media
from video import Video
from audio import Audio
import subprocess

class MediaEditor(object):

    VIDEO_BITRATE_RATIO = 0.85
    AUDIO_BITRATE_RATIO = 0.15

    def __init__(self, media: Media):
        self._media = media

        self._video_streams = media.video_streams
        self._audio_streams = media.audio_streams
        self._command = []

        self._duration = self._media.duration
        self._start_point = 0
        self._end_point = self._duration
        self._re_encode = False
        self._two_pass = False

    ## Properties
    
    #getters
    def get_media(self):
        return self._media
    
    def get_video_streams(self):
        return self._video_streams
    
    def get_audio_streams(self):
        return self._audio_streams
    
    def get_duration(self):
        return self._duration
    
    def get_start_point(self):
        return self._start_point
    
    def get_end_point(self):
        return self._end_point
    
    def get_re_encode(self):
        return self._re_encode
    
    def get_two_pass(self):
        return self._two_pass
    
    #setters
    def set_media(self, media: Media):
        self._media = media
        self.set_duration(self._media.duration)

    def set_duration(self, duration: float):
        if duration > self._media.duration:
            self._end_point = self._media.duration
            self._duration = self._end_point - self._start_point
        else:
            self._end_point = self._start_point + duration
            self._duration = duration

    def set_start_point(self, start_point: float):
        if start_point < 0:
            self._start_point = 0
        elif start_point >= self._media.duration:
            raise ValueError('Start point cannot be greater than or equal to the duration of the media.')
        else:
            self._start_point = start_point
        self._duration = self._end_point - self._start_point

    def set_end_point(self, end_point: float):
        if end_point < 0:
            raise ValueError('End point cannot be less than 0.')
        elif end_point >= self._media.duration:
            self._end_point = self._media.duration
        else:
            self._end_point = end_point
        self._duration = self._end_point - self._start_point

    def set_re_encode(self, re_encode: bool):
        self._re_encode = re_encode

    def set_two_pass(self, two_pass: bool):
        self._two_pass = two_pass
    
    media = property(get_media, set_media)
    video_streams = property(get_video_streams)
    audio_streams = property(get_audio_streams)
    duration = property(get_duration, set_duration)
    start_point = property(get_start_point, set_start_point)
    end_point = property(get_end_point, set_end_point)
    re_encode = property(get_re_encode, set_re_encode)

    ## Private methods
    def _build_command(self):
        self._command = ['ffmpeg', '-y', '-ss', str(self._start_point), '-to', str(self._end_point), '-i', self._media.path, '-v', 'quiet', '-stats']

        if self._re_encode:
            self._command += ['-c:v', 'libx264', '-c:a', 'aac', '-strict', '2', '-filter_complex']
            self._command += self._build_filter_complex()
            self._command += self._build_bitrates()
            self._command += self._build_mapping_with_filter_complex()
        else:
            self._command += ['-c', 'copy']
            self._command += self._build_mapping()

        return self._command

    def _build_filter_complex(self):
        filter_complex = ''

        for stream in range(len(self._video_streams)):
            if self._video_streams[stream] != None:
                filter_complex += '[' + '0:v:' + str(stream) + ']'
                filter_complex += f'scale={self._video_streams[stream].width}:{self._video_streams[stream].height},'
                filter_complex += f'fps={int(self._video_streams[stream].fps)}'
                filter_complex += f'[v{stream}];'

        for stream in range(len(self._audio_streams)):
            if self._audio_streams[stream] != None:
                filter_complex += '[' + '0:a:' + str(stream) + ']'
                filter_complex += f'volume={self._audio_streams[stream].volume}'
                filter_complex += f'[a{stream}];'

        return [filter_complex]
    
    def _build_bitrates(self):
        bitrates = []

        for stream in range(len(self._video_streams)):
            if self._video_streams[stream] != None:
                bitrates += ['-b:v:' + str(stream), str(self._video_streams[stream].bitrate)]

        for stream in range(len(self._audio_streams)):
            if self._audio_streams[stream] != None:
                bitrates += ['-b:a:' + str(stream), str(self._audio_streams[stream].bitrate)]

        return bitrates
    
    def _build_mapping_with_filter_complex(self):
        mapping = []

        for stream in range(len(self._video_streams)):
            if self._video_streams[stream] != None:
                mapping += ['-map', '[v' + str(stream) + ']']

        for stream in range(len(self._audio_streams)):
            if self._audio_streams[stream] != None:
                mapping += ['-map', '[a' + str(stream) + ']']

        return mapping
    
    def _build_mapping(self):
        mapping = ['-c', 'copy']

        for stream in range(len(self._video_streams)):
            if self._video_streams[stream] != None:
                mapping += ['-map', '0:v:' + str(stream)]

        for stream in range(len(self._audio_streams)):
            if self._audio_streams[stream] != None:
                mapping += ['-map', '0:a:' + str(stream)]

        return mapping

    ## Public methods

    def trim(self, start_point: float, end_point: float):
        self.start_point = start_point
        self.end_point = end_point

    def disable_video_stream(self, stream: int):
        self._video_streams[stream] = None

    def disable_audio_stream(self, stream: int):
        self._audio_streams[stream] = None

    def enable_video_stream(self, stream: int):
        self._video_streams[stream] = self._media.video_streams[stream]

    def enable_audio_stream(self, stream: int):
        self._audio_streams[stream] = self._media.audio_streams[stream]

    def flatten(self):
        """Disables all streams except the first video stream and the first audio stream."""
        for stream in range(len(self._video_streams)):
            if stream != 0:
                self.disable_video_stream(stream)

        for stream in range(len(self._audio_streams)):
            if stream != 0:
                self.disable_audio_stream(stream)

    def set_video_bitrate(self, bitrate: int, stream: int = 0):
        self.re_encode = True
        self._video_streams[stream].bitrate = bitrate

    def set_audio_bitrate(self, bitrate: int, stream: int = 0):
        self.re_encode = True
        self._audio_streams[stream].bitrate = bitrate

    def set_sseof(self, sseof: float):
        self.end_point = self._media.duration
        self.start_point = self.end_point - sseof

    def compress(self, bitrate: int):
        self._re_encode = True
        
        enabled_video_streams = [stream for stream in self._video_streams if stream != None]
        enabled_audio_streams = [stream for stream in self._audio_streams if stream != None]

        video_bitrate = bitrate * self.VIDEO_BITRATE_RATIO
        audio_bitrate = bitrate * self.AUDIO_BITRATE_RATIO

        bitrate_per_video_stream = video_bitrate / len(enabled_video_streams)
        bitrate_per_audio_stream = audio_bitrate / len(enabled_audio_streams)

        for stream in range(len(self._video_streams)):
            if self._video_streams[stream] != None:
                self.set_video_bitrate(bitrate_per_video_stream, stream)

        for stream in range(len(self._audio_streams)):
            if self._audio_streams[stream] != None:
                self.set_audio_bitrate(bitrate_per_audio_stream, stream)

    def compress_to_filesize(self, filesize: int):
        """Compresses the media to the specified filesize in bytes.
        NOTE: This method enables two-pass encoding which doubles the time it takes to compress the media.
        """
        bitrate = (filesize * 8 / self._duration) * 0.975
        self._two_pass = True
        self.compress(bitrate)

    def compress_to_filesize_mb(self, filesize: int):
        """Compresses the media to the specified filesize in megabytes.
        NOTE: This method enables two-pass encoding which doubles the time it takes to compress the media.
        """
        self.compress_to_filesize(filesize * 1000 * 1000)


    #### Video Filters ####
    def change_fps(self, fps: float, stream: int = 0):
        self.re_encode = True
        self._video_streams[stream].fps = fps
        
    def change_height(self, height: int, stream: int = 0):
        self.re_encode = True
        self._video_streams[stream].height = height

    def change_width(self, width: int, stream: int = 0):
        self.re_encode = True
        self._video_streams[stream].width = width

    def change_resolution(self, width: int, height: int, stream: int = 0):
        self.re_encode = True
        self._video_streams[stream].width = width
        self._video_streams[stream].height = height
    
    #### Audio Filters ####
    def change_volume(self, volume: float, stream: int = 0):
        self.re_encode = True
        self._audio_streams[stream].volume = volume

    def mute(self, stream: int = 0):
        self.re_encode = True
        self._audio_streams[stream].volume = 0

    #### Export ####
    def export(self, output: str) -> 'Media':
        """Exports the media to the specified output."""
        self._build_command()

        if self._two_pass:
            #first pass
            first_pass_command = self._command + ['-pass', '1', '-f', 'mp4', 'NUL']
            p = subprocess.Popen(first_pass_command)
            p.wait()
            print('Pass 1 complete')

            #second pass
            self._command += ['-pass', '2', output]
            p = subprocess.Popen(self._command)
            p.wait()
        else:
            self._command += [output]
            p = subprocess.Popen(self._command)
            p.wait()

        #return new media object
        print('Exported to ' + output)
        return Media(output)

if __name__ == "__main__":
    media = Media('Replay 2023-12-25 22-31-45.mp4')

    media_editor = MediaEditor(media)
    media_editor.trim(0, 10)
    media_editor.flatten()
    media_editor.compress_to_filesize_mb(25)
    media_editor.export('test.mp4')

