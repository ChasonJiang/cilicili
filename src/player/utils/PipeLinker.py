import logging
from multiprocessing.connection import PipeConnection
from time import sleep
from PyQt5.QtCore import *
import numpy as np
LOGGER=logging.getLogger()

class PipeLinker(QObject):
    def __init__(self, decoder, outPipe:PipeConnection, frameShape:list):
        super(PipeLinker, self).__init__()
        self.decoder = decoder
        self.outPipe = outPipe
        self.frameShape = frameShape # (H, W, C)
        
        self.isQuit = False

    def quit(self):
        self.isQuit = True

    def work(self):
        read_size = self.frameShape[0] *\
                    self.frameShape[1] *\
                    self.frameShape[2]
        while not self.isQuit:
            LOGGER.debug("read frame")
            frame_bytes=self.decoder.stdout.read(read_size)
            if not frame_bytes:
                self.outPipe.send(None)
                break
            frame = (
                np
                .frombuffer(frame_bytes, np.uint8)
                .reshape(self.frameShape)
            )
            LOGGER.debug("send frame")
            self.outPipe.send(frame)
            # sleep(0.1)
            
            
