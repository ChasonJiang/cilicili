import logging
from PyQt5.QtCore import *
from threading import Thread
from .SRContext import SRContext
from .SRStatusCode import SRStatusCode
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
            try:
                frames = self.inferencer.process(self.frame_buffer_queue)
            except Exception as e:
                LOGGER.debug("Inferencer except")
                LOGGER.debug(e)
                self.sr_context.msgPipe.send(SRStatusCode.SRException)
                # self.sr_context.outputDataPipe.send(None)
                break


            if frames is None:
                LOGGER.debug("SRWorker process over")
                self.sr_context.outputDataPipe.send(None)
                break

            for frame in frames:
                # print("send")
                self.sr_context.outputDataPipe.send(frame)
        LOGGER.debug("SRWorker quited")