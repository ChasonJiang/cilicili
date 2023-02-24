import logging
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ..Ui.Ui_PlayerControlLayer import Ui_playerControlLayer

LOGGER=logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class PlayerControlLayer(QWidget,Ui_playerControlLayer):
    size_follow_parent = pyqtSignal(QRect)
    move_follow_parent = pyqtSignal(QPoint)
    to_show = pyqtSignal(int)
    show_full_screen = pyqtSignal(bool)
    switch_play_state = pyqtSignal(bool)
    upadte_play_progress = pyqtSignal(int)
    set_duration_time = pyqtSignal(int)
    seek_to = pyqtSignal(int)
    switch_sr_mode = pyqtSignal(bool)

    def __init__(self,parent=None):
        super(PlayerControlLayer, self).__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        # self.setStyleSheet("*{\n"
        #                     "background-color: rgba(0,0,0,0);\n"
        #                     "}")

        self.setAttribute(Qt.WA_DeleteOnClose)
        # self.setAttribute(Qt.WA_Hover, True)
        self.size_follow_parent.connect(self.sizeFollowParent)
        self.to_show.connect(self.toShow)
        self.setMouseTracking(True)
        self.setupUi(self)
        self.playControlBar.setAttribute(Qt.WA_Hover, True)
        self.playControlBar.installEventFilter(self)
        self.playControlBar.hide()
        self.playStatusBar.hide()
        

        ###### sr control ######
        self.superResolutionButton.setCheckable(True)
        self.superResolutionButton.clicked[bool].connect(self.switchSRMode)
        
        ###### play control ######
        self.isShow = False
        self.playButton.setCheckable(True)
        self.playButton.clicked[bool].connect(self.switchPlayState)
        self.playState = True
        self.fullScreenButton.setCheckable(True)
        self.fullScreenButton.clicked[bool].connect(self.switchFullScreen)
        self.isHover = False
        self.timerIsQuit = False

        self.seekSlider.setTickInterval(1)
        self.seekSlider.sliderPressed.connect(self.seekTo)
        self.durationTime = 0.0
        self.upadte_play_progress.connect(self.updatePlayProgress)
        self.set_duration_time.connect(self.setDurationTime)

        self.srmode = False

    def eventFilter(self, widget:QObject, event:QEvent) -> bool:
        # print(event)
        evet_type = event.type()
        if widget == self.playControlBar:
            if evet_type ==  QEvent.HoverEnter:
                self.isHover = True
                return True
            elif evet_type == QEvent.HoverLeave:
                self.isHover = False
                if self.timerIsQuit:
                    self.playControlBar.hide()
                    self.playStatusBar.hide()
                    # self.hide()
                    self.isShow = False
                return True
        return super().eventFilter(widget, event)

    def seekTo(self,):
        # print(self.seekSlider.value())
        self.seek_to.emit(self.seekSlider.value())

    def switchPlayState(self,state:bool):
        self.playState = not state
        self.switch_play_state.emit(self.playState)

    def switchSRMode(self,state:bool):
        self.switch_sr_mode.emit(state)


    def updatePlayProgress(self,t:int):
        self.seekSlider.setValue(t)
        self.playProgressInfo.setText(" / ".join([self.timeCost(t),self.timeCost(self.durationTime)]))
        
    def timeCost(self, ts:int):
        '''
            Args:
            ts(int): ms

            Return: String 'HH:MM:SS'
                
        '''
        m, s = divmod(round(ts/1000), 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d" % (h, m, s)

    def setDurationTime(self,t:int):
        self.durationTime = t
        self.seekSlider.setMinimum(0)
        self.seekSlider.setMaximum(t)

    def switchFullScreen(self,state:bool):
        if state:
            desktop = QApplication.desktop()
            self.lastRect = self.rect()
            self.setGeometry(0,0,desktop.width(),desktop.height())
        else:
            self.setGeometry(self.lastRect)

        self.show_full_screen.emit(state)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:
            self.fullScreenButton.setChecked(True)
            self.switchFullScreen(True)
        elif event.key() == Qt.Key_Escape:
            self.fullScreenButton.setChecked(False)
            self.switchFullScreen(False)

    def mousePressEvent(self,event):
        self.playButton.setChecked(not self.playButton.isChecked())
        self.switchPlayState(self.playState)
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.to_show.emit(2000)
        return super().mouseMoveEvent(event)

    def moveFollowParent(self,qpoint:QPoint):
        self.move(qpoint)


    def sizeFollowParent(self,qRect:QRect):
        # self.move(qRect.x(),qRect.y())
        # self.setFixedSize(qRect.width(),qRect.height())
        self.setGeometry(qRect)
        # self.update()

    def hideBar(self):

        if not self.isHover:
            self.playControlBar.hide()
            self.playStatusBar.hide()
            # self.hide()
            self.isShow = False
        self.timerIsQuit = True



    def toShow(self, timeout:int=1000):
        '''
            Args:
                timeout(int): The number of seconds to show ,unit ms.
        '''
        
        if not self.isShow:
            self.timeout= timeout
            self.playControlBar.show()
            self.playStatusBar.show()
            # self.show()
            self.isShow = True
            self.timerIsQuit = False
            self.timer = QTimer()
            self.timer.singleShot(timeout,self.hideBar)
        


