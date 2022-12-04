import logging
from queue import Queue
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from player.PlayerControlLayer import PlayerControlLayer

from .utils.AudioDevice import AudioDevice
from .DisplayLayer import DisplayLayer
from .utils.PlayWorker import PlayWorker
from .utils.MediaInfo import MediaInfo
from .utils.VideoContext import VideoContext
from .utils.VideoDecodeWorker import VideoDecodeWorker
from .utils.VideoPlayWorker import VideoPlayWorker
from .assets.player_assets import *
logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO) # DEBUG
LOGGER=logging.getLogger()

class BasePlayer(QWidget):
    decoder_work_signal  = pyqtSignal()
    video_play_signal = pyqtSignal()
    play_pause_signal = pyqtSignal()
    play_resume_signal = pyqtSignal()
    def __init__(self, parent=None):
        super(BasePlayer, self).__init__(parent=parent)
        LOGGER.info("init BasePlayer")
        self.displayLayer=DisplayLayer(self)
        self.playerControlLayer=PlayerControlLayer(self)
        self.setMouseTracking(True)
        self.displayLayer.setMouseTracking(True)
        self.playerControlLayer.setMouseTracking(True)
        self.installEventFilter(self.playerControlLayer)
        self.setMouseTracking(True)
        self.setupUi()

        # self.playWorker = None
        self.playStatus = True
        self.audioDevice = AudioDevice()
        # media_info=MediaInfo(["assets\\5s.mkv", "assets\\5s.mkv"],["assets\\5s.mkv", "assets\\5s.mkv"],"file")

        # self.play(media_info)

    def play(self, media_info=None):
        # print("thread id of BasePlayer is {}".format(QThread.currentThreadId()))   
        # self.playWorker =None 
        self.playThread = QThread()
        self.playWorker = PlayWorker(self.displayLayer,self.audioDevice)
        self.playWorker.moveToThread(self.playThread)
        # self.play_pause_signal.connect(self.playWorker.pause)
        # self.play_resume_signal.connect(self.playWorker.resume)
        # self.playWorker.play_pause_signal.connect(self.playWorker.pause)
        # self.playWorker.play_resume_signal.connect(self.playWorker.resume)
        self.playThread.started.connect(lambda:self.playWorker.play(media_info))
        self.playThread.finished.connect(lambda:self.quitPlayThread)
        self.playThread.start()
        self.playStatus = True
        # print("hjkgdfjhd")

    def mouseMoveEvent(self, event):
        self.playerControlLayer.to_show.emit(800)
        return super().mouseMoveEvent(event)

    def quitPlayThread(self):
        LOGGER.info("quit PlayThread")
        self.playThread.quit()
        self.playThread.wait()


    def mousePressEvent(self,event):
        # print("mouse press")
        self.switchPlayState()
        return super().mousePressEvent(event)

    def switchPlayState(self):
        self.playStatus = not self.playStatus
        if self.playStatus:
            # print("emit play_resume_signal")
            # self.play_resume_signal.emit()
            self.playWorker.play_resume_signal.emit()
            # self.playWorker.resume()
        else:
            # print("emit play_pause_signal")
            # self.play_pause_signal.emit()
            self.playWorker.play_pause_signal.emit()
            # self.playWorker.pause()

    def __del__(self,):
        self.playThread.quit()
        self.playThread.wait()

    def close(self):
        # self.playerControlLayer.close()
        super().close()
        
    def resizeEvent(self, event: QResizeEvent):
        # QCoreApplication.postEvent(self.playerControlLayer, event)
        self.playerControlLayer.size_follow_parent.emit(QRect(0,0, event.size().width(),event.size().height()))
        # self.playerControlLayer.event(event)
        return super().resizeEvent(event)

    def setupUi(self,):
        self.setWindowTitle("BasePlayer")
        self.setObjectName("BasePlayer")
        self.resize(1920,1080)
        self.setMinimumSize(1620,987)
        # 隐藏窗口边框
        # self.setWindowFlag(Qt.FramelessWindowHint, True)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # self.displayLayer.setDisplayMode(16.0/9)
        self.layout.addWidget(self.displayLayer)


        # self.setGeometry(0,0,600,600







if __name__ == "__main__":
    media_info=MediaInfo(["assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv"],[],"file")
    app = QApplication(sys.argv)
    player = BasePlayer(media_info=media_info)
    player.show()

    sys.exit(app.exec_())
