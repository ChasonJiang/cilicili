from time import sleep
import time
from PyQt5.QtCore import *
from pyaudio import *

class AudioDevice(QObject):
    def __init__(self,):
        super(AudioDevice, self).__init__()
        self.audioDevice = PyAudio()
        self.stream = self.audioDevice.open(format=self.audioDevice.get_format_from_width(2),
                                            frames_per_buffer=1600,
                                            channels=2, 
                                            rate=48000, 
                                            output=True, 
                                            stream_callback=self.callback)
        self.curr_frame = bytes("")
        self.stream.start_stream()


    def callback(self, in_data, frame_count, time_info, status):
        return (self.curr_frame, paContinue)

    def update(self, chunk):
        self.curr_frame = chunk

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        del self.stream
        del self.audioDevice









if __name__ == '__main__':
    ad = AudioDevice()
    counter = 0
    # audioDevice = PyAudio()
    # stream = audioDevice.open(format=audioDevice.get_format_from_width(2),
    #                                     channels=2, 
    #                                     rate=48000, 
    #                                     output=True, )
    with open("C:\\Users\\White\\Project\\rtsr_client_pyqt\\out.pcm","rb") as f:
        # while True:
        #     stream.write(f.read())
        while True:
            counter += 1
            start_time =time.time()
            ad.update(f.read(round(16 * 48000 * 2 /8 * (1.0/30))))
            sleep(0.020)
            # sleep(0.001)
            print("frame time: {:3f} seconds | frame: {} | byte size: {}".format((time.time()-start_time)*1000,counter,round(16 * 48000 * 2 /8 * (1.0/30))))

