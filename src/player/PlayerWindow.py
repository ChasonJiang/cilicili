import logging
from queue import Queue
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qasync import asyncSlot

from CiliCili.VideoInfo.VideoInfo import VideoInfo

from .CiliCiliPlayer import CiliCiliPlayer
from .utils.MediaInfo import MediaInfo
from SuperResolution.SRContext import SRContext
from .ui.PlayerWindow_UI import Ui_PlayerWindow
from PyQt5.QtRemoteObjects import QRemoteObjectNode
# logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.DEBUG) # DEBUG
LOGGER=logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)



class PlayerWindow(QWidget,Ui_PlayerWindow):
    switch_full_screen_signal = pyqtSignal(bool)
    def __init__(self,parent=None,srContext:SRContext=None):
        super(PlayerWindow, self).__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.srContext:SRContext = srContext
        self.CiliCiliPlayer = CiliCiliPlayer(self,srContext)
        self.setupUi(self,self.CiliCiliPlayer)
        self.CloseButton.clicked.connect(self._close)
        self.switch_full_screen_signal.connect(self.switchFullScreen)

        # 与MianWindow建立通信
        self.node = QRemoteObjectNode(parent=self)
        self.node.connectToNode(QUrl("local:MainWindow"))

        self.host = self.node.acquireDynamic('MainWindow')
        self.host.initialized.connect(self.onInitialized)

        self.videoInfo:VideoInfo = VideoInfo()
        self.curr_cid = None
        self.currentMediaInfoDict = None
        self.setMouseTracking(True)
        self.TopBar.setMouseTracking(True)
        self.Container.setMouseTracking(True)
        self.InfoContainer.setMouseTracking(True)
        self.scrollArea.setMouseTracking(True)
        self.scrollAreaWidgetContents.setMouseTracking(True)
        self.TopBar.installEventFilter(self)
        # self.Container.installEventFilter(self)
        self.InfoContainer.installEventFilter(self)
        self.scrollArea.installEventFilter(self)
        self.scrollAreaWidgetContents.installEventFilter(self)
        self.resizeBorderThreshold = 4
        self.mouseTriggerReset()


    def onInitialized(self):
        self.host.to_play_signal.connect(self.toShow)
        self.host.close_palyer_window_signal.connect(self.close)

    @asyncSlot(dict)
    async def toShow(self,params:dict):
        # if self.isHidden():
            # self.setHidden(False)
            # self.raise_()
            # self.setWindowFlag(Qt.WindowStaysOnTopHint,True)
        # if not self.isActiveWindow():
        #     self.activateWindow()
        self.setWindowFlag(Qt.WindowStaysOnTopHint,True)
        self.show()
        self.setWindowFlag(Qt.WindowStaysOnTopHint,False)
        self.show()
            # self.raise_()
            # self.setWindowFlag(Qt.WindowStaysOnTopHint,False)
        self.initVideoInfo(params)
    

    @asyncSlot(dict)
    async def initVideoInfo(self,params:dict):
        LOGGER.debug(f"video info:\n{params}")
        aid = params['aid']
        bvid = params['bvid']
        credential=params['credential']
        cid = params['cid']

        self.videoInfo.init(aid=aid,bvid=bvid,credential=credential)
        await self.videoInfo.requestInfo(bvid=bvid,
                                        aid=aid,
                                        credential=credential)

        await self.toPlay(cid=cid)

    @asyncSlot()
    async def toPlay(self,cid:int=None,page_index:int=None):
        self.currentMediaInfoDict = await self.videoInfo.createMediaInfo(cid=cid,page_index=page_index)
        id = self.currentMediaInfoDict["defult"]
        video_url=self.currentMediaInfoDict["media_info"][id][0].video_url
        LOGGER.debug(f"video link:\n{video_url}")
        self.play(self.currentMediaInfoDict["media_info"][id][0])

        
    def play(self,media_info:MediaInfo):
        self.CiliCiliPlayer.play_signal.emit(media_info)


    def switchFullScreen(self,state:bool):
        if state:
            self.TopBar.setHidden(True)
            self.InfoContainer.setHidden(True)
            self.showFullScreen()
        else:
            self.TopBar.setHidden(False)
            self.InfoContainer.setHidden(False)
            self.showNormal()

    # def closeEvent(self, e:QCloseEvent) -> None:
    #     self.setHidden(True)

    def _close(self):
        self.setHidden(True)
        self.CiliCiliPlayer.pause_signal.emit()
        
    def eventFilter(self, w: QObject, e: QEvent) -> bool:
        if w in [self.TopBar, self.InfoContainer, self.scrollArea, self.scrollAreaWidgetContents]:
            e_type = e.type()
            if e_type == QEvent.Type.MouseButtonPress:
                if e.button() == Qt.LeftButton:
                    self.is_pressed = True
                    self.mousePressEvent(e)
                    # if w == self.Container:
                    #     self.Container.mousePressEvent(e)
                    
        return super().eventFilter(w,e)

    def mouseTriggerReset(self):
        # self.is_pressed = False
        self.top_drag = False
        self.bottom_drag = False
        self.left_drag = False
        self.right_drag = False
        self.window_move = False
        # self.is_move = False
        self.is_resize = False
        self.is_pressed = False

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if self.is_pressed:
            if e.windowPos().y() - self.resizeBorderThreshold <= 0:
                self.left_drag = False
            elif(self.height()-e.windowPos().y() - self.resizeBorderThreshold <= 0):
                self.right_drag = True

            elif e.windowPos().x() - self.resizeBorderThreshold <= 0:
                self.top_drag = False
            elif (self.width()-e.windowPos().x() - self.resizeBorderThreshold <= 0):
                self.bottom_drag = True
            elif e.windowPos().y()<=self.TopBar.height():
                self.window_move = True
            self.relativePos = e.windowPos()
            self.absolutePos = e.globalPos()
            return e.accept()
        else:
            return super().mousePressEvent(e)

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        # print(e.windowPos())
        if not self.isFullScreen():
            # if e.windowPos().y() - self.resizeBorderThreshold <= 0 or \
                # (self.height()-e.windowPos().y() - self.resizeBorderThreshold <= 0):
            if (self.height()-e.windowPos().y() - self.resizeBorderThreshold <= 0):
                self.setCursor(Qt.SizeVerCursor)
            # elif e.windowPos().x() - self.resizeBorderThreshold <= 0 or \
            #     (self.width()-e.windowPos().x() - self.resizeBorderThreshold <= 0):
            elif (self.width()-e.windowPos().x() - self.resizeBorderThreshold <= 0):
                self.setCursor(Qt.SizeHorCursor) 
            else:
                self.setCursor(Qt.ArrowCursor)
            if self.is_pressed:
                if self.right_drag or self.bottom_drag:
                    # w = e.pos().x() if e.pos().x()<0 or e.pos().x()>self.width() else self.width()
                    # h = e.pos().y() if e.pos().y()<0 or e.pos().y()>self.height() else self.height()
                    # self.resize(w,h)
                    self.resize(e.pos().x(),e.pos().y())
                    
                elif self.window_move and not (self.right_drag or self.bottom_drag):
                    pos = e.globalPos() - self.relativePos
                    self.move(round(pos.x()), round(pos.y()))
            else:
                return super().mouseMoveEvent(e)
        else:
            return super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if self.is_pressed and not self.isFullScreen():
            self.mouseTriggerReset()
        else:
            return super().mouseReleaseEvent(e)

    # @asyncSlot()
    # async def receiveCmd(self):
    #     while True:
            
        