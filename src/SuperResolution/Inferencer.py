from PyQt5.QtCore import *
# from abc import abstractmethod, ABCMeta
# from multiprocessing.connection import PipeConnection

# class Inferencer(QObject, metaclass=ABCMeta):
#     @abstractmethod
#     def process(self, frame):
#         pass

class Inferencer(QObject):
    
    def process(self, frame):
        pass