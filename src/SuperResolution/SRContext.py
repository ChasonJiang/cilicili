

from multiprocessing.connection import PipeConnection


class SRContext():
    def __init__(self, cmdPipe, msgPipe, inputDataPipe, outputDataPipe):
        assert isinstance(cmdPipe,PipeConnection)
        assert isinstance(msgPipe,PipeConnection)
        assert isinstance(inputDataPipe,PipeConnection)
        assert isinstance(outputDataPipe,PipeConnection)
        self.cmdPipe= cmdPipe
        self.msgPipe= msgPipe
        self.inputDataPipe= inputDataPipe
        self.outputDataPipe= outputDataPipe