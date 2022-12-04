
from multiprocessing.connection import PipeConnection
from time import sleep
from SuperResolution.Inferencer import Inferencer


class FSRCNN(Inferencer):
    def __init__(self,):
        pass

    def process(self, in_pipe: PipeConnection, out_pipe: PipeConnection):
        print("FSRCNN process image ...")
        frame=in_pipe.recv()
        out_pipe.send(frame)
        sleep(0.001)
        # sleep(1)