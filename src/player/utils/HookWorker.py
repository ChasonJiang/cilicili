from multiprocessing.connection import PipeConnection

from PyQt5.QtCore import *

class HookWorker(QObject):
    def __init__(self,inputPipe, outputPipe,srContext):
        super(HookWorker, self).__init__()
        assert isinstance(inputPipe,PipeConnection)
        self.inputPipe = inputPipe
        self.outputPipe = outputPipe
        self.srContext = srContext


    def work(self):
         