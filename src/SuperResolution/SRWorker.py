from multiprocessing.connection import PipeConnection
from time import sleep
from PyQt5.QtCore import *

from .SRContext import SRContext

from .Inferencer import Inferencer
from .SRStatusCode import SRStatusCode as SRSC

class SRWorker(QObject):
    def __init__(self, inferencer,srContext):
        super(SRWorker, self).__init__()
        assert isinstance(inferencer,Inferencer)
        # assert isinstance(inPipe,PipeConnection)
        # assert isinstance(outPipe,PipeConnection)
        assert isinstance(srContext,SRContext)
        self.inferencer = inferencer
        # self.inPipe = inPipe
        # self.outPipe = outPipe
        # self.frameSize = frameSize
        self.srContext = srContext
        self.isQuit = False

    def quit(self):
        self.isQuit= True

    def inference(self):
        self.srContext.msgPipe.send(SRSC.InferencerStarted)
        while True:
            if self.isQuit:
                self.srContext.outputDataPipe.send(None)
                break
            fream=self.srContext.inputDataPipe.recv()
            self.srContext.outputDataPipe.send(fream)
            print("received")
            
            # self.inferencer.process(self.srContext.inputDataPipe, self.srContext.outputDataPipe)
        
        print("inference over")

