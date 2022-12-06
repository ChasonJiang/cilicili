
from multiprocessing.connection import PipeConnection
from time import sleep
from SuperResolution.Inferencer import Inferencer
import numpy as np

class FSRCNN(Inferencer):
    def __init__(self,):
        pass

    def process(self, frame):
        # print("FSRCNN process image ...")
        sleep(0.001)
        return frame
        # sleep(1)