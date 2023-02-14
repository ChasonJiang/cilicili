from PyQt5.QtCore import *

class PlayStatusController(QObject):
    update_status = pyqtSignal(bool)
    def __init__(self,):
        super(PlayStatusController, self).__init__()
        self.locker = QMutex()
        self.audio_wait = False
        self.video_wait = False
        self.video_full = False
        self.audio_full = False
        self.in_period = False


    # 此函数将手动发起缓冲等待信号
    def wait_buffer_mode(self,):
        self.locker.lock()
        self.audio_wait = True
        self.video_wait = True
        self.audio_full = False
        self.video_full = False
        self.in_period = True
        self.locker.unlock()


    def audio_wait_buffer_slot(self):
        self.locker.lock()
        if not self.in_period:
            self.in_period = True
            self.audio_wait = True
            if not self.video_wait:
                self.send_not_ready()
        else:
            self.audio_wait = True
        self.locker.unlock()

    def audio_buffer_full_slot(self,):
        self.locker.lock()
        if self.in_period:
            self.audio_full = True
            if self.video_full:
                self.send_ready()
        # else:
        #     # self.in_period = True
        #     self.audio_full = True
        self.locker.unlock()

    def video_wait_buffer_slot(self):
        self.locker.lock()
        if not self.in_period:
            # self.in_period = True
            self.video_wait = True
            if not self.audio_wait:
                self.send_not_ready()
        else:
            self.video_wait = True
        self.locker.unlock()

    def video_buffer_full_slot(self,):
        self.locker.lock()
        if self.in_period:
            self.video_full = True
            if self.audio_full:
                self.send_ready()
        # else:
        #     # self.in_period = True
        #     self.video_full = True
        self.locker.unlock()

    def reset(self):
        self.video_full = False
        self.audio_full = False
        self.video_wait = False
        self.audio_wait = False
        self.in_period = False

    def send_ready(self):
        # self.locker.lock()
        self.update_status.emit(True)
        self.reset()
        # self.locker.unlock()

    def send_not_ready(self):
        # self.locker.lock()
        self.update_status.emit(False)
        # self.locker.unlock()