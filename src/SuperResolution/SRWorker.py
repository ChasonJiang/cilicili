import json
import logging
from multiprocessing.connection import PipeConnection
import os
# from queue import Queue
from multiprocessing import Queue
# from torch.multiprocessing import Queue
from time import sleep
from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *
from threading import Thread
import ffmpeg
import numpy as np
from SuperResolution.ClassLoader import classLoader

from player.utils.VideoContext import VideoContext

from .SRContext import SRContext

from .Inferencer import Inferencer
from .SRStatusCode import SRStatusCode as SRSC
LOGGER=logging.getLogger()

# class SRWorker(QObject):
class SRWorker(Thread):
    def __init__(self, frame_buffer_queue:Queue, inferencer:Inferencer, sr_context:SRContext):
        super(SRWorker, self).__init__()
        self.frame_buffer_queue = frame_buffer_queue
        self.sr_context = sr_context
        self._isQuit = False
        self.inferencer = inferencer

    def quit(self):
        self._isQuit = True

    def run(self):
        while True:
            if self._isQuit:
                print("SRWorker quit")
                break
            frames = self.inferencer.process(self.frame_buffer_queue)

            if frames is None:
                print("SRWorker process over")
                break

            for frame in frames:
                self.sr_context.outputDataPipe.send(frame)
