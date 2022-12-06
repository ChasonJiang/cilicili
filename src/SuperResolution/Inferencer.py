from abc import abstractmethod, ABCMeta
from multiprocessing.connection import PipeConnection

class Inferencer(metaclass=ABCMeta):
    @abstractmethod
    def process(self, frame):
        pass