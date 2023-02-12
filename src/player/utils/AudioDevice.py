from PyQt5.QtCore import *
from pyaudio import *

class AudioDevice(QObject):
    def __init__(self,):
        super(AudioDevice, self).__init__()
        self.audioDevice = PyAudio()
        self.stream = self.audioDevice.open(format=self.audioDevice.get_format_from_width(2), channels=2, rate=192000, output=True)
        


    def update(self, chunk):
        self.stream.write(chunk)

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        del self.stream
        del self.audioDevice

# class AudioDevice(QObject):
#     def __init__(self,):
#         super(AudioDevice, self).__init__()
#         self.audioDevice = PyAudio()
#         self.stream = self.audioDevice.open(format=self.audioDevice.get_format_from_width(2),
#                                             frames_per_buffer=1600,
#                                             channels=2, 
#                                             rate=48000, 
#                                             output=True, 
#                                             stream_callback=self.callback)
#         self.curr_frame = bytes([0 for i in range(2*16*1000)])
#         self.stream.start_stream()


#     def callback(self, in_data, frame_count, time_info, status):
#         return (self.curr_frame, paContinue)

#     def update(self, chunk):
#         self.curr_frame = chunk

#     def __del__(self):
#         self.stream.stop_stream()
#         self.stream.close()
#         del self.stream
#         del self.audioDevice

