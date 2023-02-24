import logging
from PyQt5.QtCore import *
from threading import Thread
from .SRContext import SRContext
from multiprocessing import Queue
from .Inferencer import Inferencer

LOGGER=logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

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
                break
            frames = self.inferencer.process(self.frame_buffer_queue)

            if frames is None:
                LOGGER.debug("SRWorker process over")
                self.sr_context.outputDataPipe.send(None)
                break

            for frame in frames:
                self.sr_context.outputDataPipe.send(frame)
        LOGGER.debug("SRWorker quited")