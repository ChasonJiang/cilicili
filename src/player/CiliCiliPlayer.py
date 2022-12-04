

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
# from .assets.player_assets import *

logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO) # DEBUG
LOGGER=logging.getLogger()

class CiliCiliPlayer(QWidget):
    decoder_work_signal  = pyqtSignal()
    video_play_signal = pyqtSignal()
    play_pause_signal = pyqtSignal()
    play_resume_signal = pyqtSignal()
    def __init__(self, parent=None,srContext=None):
        super(CiliCiliPlayer, self).__init__(parent=parent)
        LOGGER.info("init BasePlayer")
        self.setupUi()
        self.playerControlLayer.switch_play_state.connect(self.switchPlayState)
        self.playerControlLayer.show_full_screen.connect(self.switchFullScreen)
        self.setMouseTracking(True)
        # self.displayLayer.setMouseTracking(True)
        # self.playerControlLayer.setMouseTracking(True)
        self.srContext = srContext
        self.playStatus = True
        self.audioDevice = AudioDevice()
        self.isSetFullScreen = False
        self.playThread = None
        self.playWorker = None


    def play(self, media_info=None):

        self.playThread = QThread()
        self.playWorker = PlayWorker(self.displayLayer,self.audioDevice)
        self.playWorker.moveToThread(self.playThread)
        self.playWorker.send_duration_time.connect(self.playerControlLayer.setDurationTime)
        self.playWorker.update_playback_progress.connect(self.playerControlLayer.updatePlayProgress)
        self.playerControlLayer.seek_to.connect(self.playWorker.seek)
        self.playThread.started.connect(lambda:self.playWorker.play(media_info))
        self.playThread.start()
        self.playStatus = True

    def switchFullScreen(self,state:bool):
        if state:
            self.isSetFullScreen = True
            self.showFullScreen()
        else:
            self.isSetFullScreen = False
            self.showNormal()

    # def mouseMoveEvent(self, event):
    #     # print("mouseMoveEvent")
    #     self.playerControlLayer.to_show.emit(2000)
    #     return super().mouseMoveEvent(event)

    # def moveEvent(self, event:QMoveEvent):
    #     self.playerControlLayer.move_follow_parent.emit(event.pos())
    #     return super().moveEvent(event)


    def shutdown(self):
        if self.playWorker is not None:
            self.playWorker.shutdown_signal.emit()
        if self.playThread is not None:
            self.playThread.quit()
            self.playThread.wait()



    # def mousePressEvent(self,event):
    #     self.switchPlayState()
    #     return super().mousePressEvent(event)

    def closeEvent(self, event:QCloseEvent) -> None:
        self.shutdown()
        return super().closeEvent(event)

    def switchPlayState(self,state:bool):
        if state:
            self.playWorker.play_resume_signal.emit()
        else:
            self.playWorker.play_pause_signal.emit()



    def resizeEvent(self, event: QResizeEvent):
        if not self.isSetFullScreen:
            if self.parent() is None:
                self.playerControlLayer.size_follow_parent.emit(QRect(0,0, event.size().width(),event.size().height()))
            else:
                self.playerControlLayer.size_follow_parent.emit(QRect(self.geometry().x(),self.geometry().y(), event.size().width(),event.size().height()))
        return super().resizeEvent(event)
        


    def setupUi(self,):
        self.setObjectName("CiliCiliPlayer")
        self.resize(1620, 987)
        self.setMinimumSize(QSize(480, 270))
        self.setStyleSheet("*{\n"
                            "background-color: rgba(0,0,0,0);\n"
                            "}")
        self.displayLayer=DisplayLayer(self)
        self.playerControlLayer=PlayerControlLayer(self)
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.addWidget(self.displayLayer)
        self.retranslateUi()
        QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("CiliCiliPlayer", "Form"))
