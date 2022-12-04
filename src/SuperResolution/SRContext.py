

from multiprocessing.connection import PipeConnection


class SRContext():
    def __init__(self, cmdPipe, msgPipe):
        assert isinstance(cmdPipe,PipeConnection)
        assert isinstance(msgPipe,PipeConnection)
        self.cmdPipe= cmdPipe
        self.msgPipe= msgPipe