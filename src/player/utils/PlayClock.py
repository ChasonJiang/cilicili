from PyQt5.QtCore import *

class PlayClock(QObject):
    upadte_progress = pyqtSignal(float)
    def __init__(self,):
        super(PlayClock, self).__init__()
        self.curr_ts = 0.0 # ms, float 
        self.mutex = QMutex()
    
    def getClock(self):
        self.mutex.lock()
        curr_ts = self.curr_ts
        self.mutex.unlock()
        return curr_ts

    def updateClock(self,ts:int):
        self.mutex.lock()
        self.curr_ts = ts
        self.upadte_progress.emit(ts)
        self.mutex.unlock()