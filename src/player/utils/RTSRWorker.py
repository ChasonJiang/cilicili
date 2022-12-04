import logging
from multiprocessing.connection import PipeConnection
from queue import Queue
from PyQt5.QtCore import *
from SuperResolution.HandlerCmd import HandlerCmd

from SuperResolution.SRContext import SRContext
from SuperResolution.SRStatusCode import SRStatusCode as SRSC
LOGGER=logging.getLogger()

class RTSRWorker(QObject):
    def __init__(self, srContext,vbufferQueue,srbufferQueue):
        super(RTSRWorker, self).__init__()
        assert isinstance(srContext,SRContext)
        assert isinstance(vbufferQueue,Queue)
        assert isinstance(srbufferQueue,Queue)
        
        self.srContext = srContext
        self.vbufferQueue = vbufferQueue
        self.srbufferQueue = srbufferQueue
        self.isQuit = False

    def quit(self):
        self.isQuit = True
    
    def work(self):
        while not self.isQuit:
            if self.isQuit:
                self.srContext.cmdPipe(HandlerCmd(HandlerCmd.Quit))
                LOGGER.debug("RTSRWorker quit")
                break
            if self.srContext.msgPipe.poll():
                self.checkMsg(self.srContext.msgPipe.recv())

            frame = self.srbufferQueue.get(frame)
            self.srContext.outputDataPipe.send(frame)
            frame = self.srContext.inputDataPipe.recv()
            LOGGER.debug("recving frame")
            if not frame:
                LOGGER.debug("RTSRWorker over")
                break
            self.vbufferQueue.put(frame)
            
    def checkMsg(self,statusCode:int):
        if statusCode == SRSC.InferencerStarted:
            LOGGER.debug("SRSC.InferencerStarted")
        elif statusCode == SRSC.IoError:
            LOGGER.debug("SRSC.IoError")
        elif statusCode == SRSC.LoadInferencerError:
            LOGGER.debug("SRSC.LoadInferencerError")
        


            