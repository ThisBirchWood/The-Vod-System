import subprocess

class Video(object):
    def __init__(self, index: int, duration: float, bitrate: int, width: int, height: int, fps: int):
        self._index = index
        self._duration = duration
        self._bitrate = bitrate
        self._width = width
        self._height = height
        self._fps = fps

    ## Properties

    #getters
    def get_index(self):
        return self._index
    
    def get_duration(self):
        return self._duration
    
    def get_bitrate(self):
        return self._bitrate
    
    def get_width(self):
        return self._width
    
    def get_height(self):
        return self._height
    
    def get_fps(self):
        return self._fps
    
    #setters
    def set_index(self, index: int):
        self._index = index

    def set_duration(self, duration: float):
        self._duration = duration

    def set_bitrate(self, bitrate: int):
        self._bitrate = bitrate

    def set_width(self, width: int):
        self._width = width

    def set_height(self, height: int):
        self._height = height

    def set_fps(self, fps: int):
        self._fps = fps

    index = property(get_index, set_index)
    duration = property(get_duration, set_duration)
    bitrate = property(get_bitrate, set_bitrate)
    width = property(get_width, set_width)
    height = property(get_height, set_height)
    fps = property(get_fps, set_fps)