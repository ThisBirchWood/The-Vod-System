import subprocess

class Audio(object):
    def __init__(self, index: int, duration: float, bitrate: int):
        self._index = index
        self._duration = duration
        self._bitrate = bitrate
        self._volume = 1

    ## Properties

    #getters
    def get_index(self):
        return self._index
    
    def get_duration(self):
        return self._duration
    
    def get_bitrate(self):
        return self._bitrate
    
    def get_volume(self):
        return self._volume
    
    #setters
    def set_index(self, index: int):
        self._index = index

    def set_duration(self, duration: float):
        self._duration = duration
        
    def set_bitrate(self, bitrate: int):
        self._bitrate = bitrate

    def set_volume(self, volume: float):
        self._volume = volume

    index = property(get_index, set_index)
    duration = property(get_duration, set_duration)
    bitrate = property(get_bitrate, set_bitrate)
    volume = property(get_volume, set_volume)