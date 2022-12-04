
from PyQt5.QtCore import *


class BinaryNeuron(QObject):
    outStatus = pyqtSignal(bool)
    def __init__(self, singleFalseSignal:bool = False ):
        super(BinaryNeuron, self).__init__()
        self.inOneStatus = False
        self.inTwoStatus = False
        self.falseStatusFlag = False
        self.singleFalseSignal = singleFalseSignal
        self.inLocker = QMutex()

    def reset(self):
        self.inOneStatus = False
        self.inTwoStatus = False
        self.falseStatusFlag = False

    def inOne(self,v:bool):
        self.inLocker.lock()
        self.inOneStatus = v
        if self.inOneStatus and self.inTwoStatus:
            self.outStatus.emit(True)
            self.reset()
        elif not self.falseStatusFlag:
            if self.singleFalseSignal:
                self.falseStatusFlag = True
            self.outStatus.emit(False)
        self.inLocker.unlock()


    def inTwo(self,v:bool):
        self.inLocker.lock()
        self.inTwoStatus = v
        if self.inOneStatus and self.inTwoStatus:
            self.outStatus.emit(True)
            self.reset()
        elif not self.falseStatusFlag:
            if self.singleFalseSignal:
                self.falseStatusFlag = True
            self.outStatus.emit(False)
        self.inLocker.unlock()
