from PyQt5.QtCore import *

class PlayStatusController(QObject):
    update_status = pyqtSignal(bool)
    def __init__(self,):
        super(PlayStatusController, self).__init__()
        self.Locker = QMutex()
        self.awbFlag = False
        self.abfFlag = False
        self.vwbFlag = False
        self.vbfFlag = False
        self.aflag = False
        self.vflag = False
        self.aready = False
        self.vready = False
        self.isSendFalse = False

    # 此函数将手动发起缓冲等待信号
    def wait_buffer_mode(self,):
        self.Locker.lock()
        self.abfFlag = False
        self.awbFlag = True
        self.vbfFlag = False
        self.vwbFlag = True
        self.aready = False
        self.vready = False
        self.send_not_ready()
        self.Locker.unlock()


    def audio_wait_buffer_slot(self):
        self.Locker.lock()
        if self.abfFlag:
            self.awbFlag = False
            self.abfFlag = False
            self.aready = True
            self.send_ready()
        else:
            self.awbFlag = True
            self.send_not_ready()
        self.Locker.unlock()

    def audio_buffer_full_slot(self,):
        self.Locker.lock()
        if self.awbFlag:
            self.abfFlag = False
            self.awbFlag = False
            self.aready = True
            self.send_ready()
        else:
            self.abfFlag = True
        
        self.Locker.unlock()

    def video_wait_buffer_slot(self):
        self.Locker.lock()
        if self.vbfFlag == True:
            self.vbfFlag = False
            self.vwbFlag = False
            self.vready = True
            self.send_ready()
        else:
            self.vwbFlag = True
            self.send_not_ready()
        self.Locker.unlock()

    def video_buffer_full_slot(self,):
        self.Locker.lock()
        if self.vwbFlag == True:
            self.vwbFlag = False
            self.vbfFlag = False
            self.vready = True
            self.send_ready()
        else:
            self.vbfFlag = True
        self.Locker.unlock()


    def send_ready(self):
        if self.aready and self.vready:
            self.update_status.emit(True)
            self.vready = False
            self.aready = False
            self.isSendFalse = False

    def send_not_ready(self):
        if not self.isSendFalse:
            self.update_status.emit(False)
            self.isSendFalse = True