from abc import abstractmethod, ABCMeta
from multiprocessing.connection import PipeConnection

class Inferencer(metaclass=ABCMeta):
    @abstractmethod
    def process(self, in_pipe:PipeConnection, out_pipe:PipeConnection):
        '''
            in_pipe(PipeConnection): a pipe connection of image, input a image ndarray, shape like (W, H, C)
            out_pipe(PipeConnection): a pipe connection of image, input a image ndarray, shape like (W, H, C)
        '''
        pass