from abc import abstractmethod, ABCMeta
from multiprocessing.connection import PipeConnection

class Inferencer(metaclass=ABCMeta):
    @abstractmethod
    def process(self, in_pipe:PipeConnection, out_pipe:PipeConnection):
        pass