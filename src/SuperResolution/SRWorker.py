from multiprocessing.connection import PipeConnection
from PyQt5.QtCore import *

from SuperResolution.Inferencer import Inferencer


class SRWorker(QObject):
    def __init__(self, inferencer, inPipe, outPipe):
        super(SRWorker, self).__init__()
        assert isinstance(inferencer,Inferencer)
        assert isinstance(inPipe,PipeConnection)
        assert isinstance(outPipe,PipeConnection)
        self.inferencer = inferencer
        self.inPipe = inPipe
        self.outPipe = outPipe
        self.isQuit = False

    def quit(self):
        self.isQuit= True

    def inference(self):
        while True:
            if self.isQuit:
                self.outPipe.send(None)
                break
            self.inferencer.process(self.inPipe,self.outPipe)

