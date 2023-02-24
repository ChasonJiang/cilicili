import json
import logging
import os
from queue import Queue
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qasync import asyncSlot
from CiliCili.VideoInfo.EpisodeInfo import EpisodeInfo

from CiliCili.VideoInfo.VideoInfo import VideoInfo
from VideoProcessor.HandlerCmd import HandlerCmd

from .CiliCiliPlayer import CiliCiliPlayer
from .Utils.MediaInfo import MediaInfo
from VideoProcessor.SRContext import SRContext
from .Ui.PlayerWindow_UI import Ui_PlayerWindow
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
        self.DescriptionBox.setHidden(True)
        self.initConnection()

        # 与MianWindow建立通信
        self.node = QRemoteObjectNode(parent=self)
        self.node.connectToNode(QUrl("local:MainWindow"))
        self.host = self.node.acquireDynamic('MainWindow')
        self.host.initialized.connect(self.onInitialized)

        self.videoInfo:VideoInfo = VideoInfo()
        self.episodeInfo:EpisodeInfo = EpisodeInfo()
        self.curr_cid = None
        self.currentMediaInfoDict = None

        self.currentPlayType = None

        self.inferencerName = None
        self.multiplier = 1
        self.loadInferencerInfo()
        self.srContext.cmdPipe.send(HandlerCmd(HandlerCmd.LoadInferencer, self.inferencerName))

        self.initMoveAndResize()

    def initConnection(self):
        self.CloseButton.clicked.connect(self._close)
        self.switch_full_screen_signal.connect(self.switchFullScreen)
        self.MinButton.clicked.connect(self.showMinimized)
        def showMax():
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
        self.MaxButton.clicked.connect(showMax)
        def extendSwitcher():
            if self.ExtendButton.text() == "展开":
                self.ExtendButton.setText("收起")
                self.DescriptionBox.setHidden(False)
            else:
                self.ExtendButton.setText("展开")
                self.DescriptionBox.setHidden(True)
        self.ExtendButton.clicked.connect(extendSwitcher)
        self.EpisodeListBox.clicked.connect(self.selectEpisode)

    def initMoveAndResize(self):
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
    
    def closeEvent(self, e: QCloseEvent) -> None:
        self.CiliCiliPlayer.close()
        return super().closeEvent(e)
    
    def loadInferencerInfo(self):
        # print("Load Inferencer Info")
        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)),"SuperResolutionInferencer","SuperResolutionInferencerRegister.json"),"r") as f:
            # with open(os.path.join(os.path.dirname(__file__),"SuperResolutionInferencer","SuperResolutionInferencerRegister.json"),"r") as f:
                self.inferencerInfo = json.loads(f.read())

            self.inferencerName = self.inferencerInfo["Default"]
            multiplier=self.inferencerInfo["Inferencer"][self.inferencerName]["Multiplier"]
            assert multiplier != 0
            self.multiplier = multiplier

            LOGGER.debug("Inferencer Info loaded")
        except IOError:
            # print("Error reading SuperResolutionInferencerRegister.json")
            LOGGER.error("Error reading SuperResolutionInferencerRegister.json")
            raise RuntimeError("Load InferencerInfo Failed")

    @asyncSlot(dict)
    async def toShow(self,params:dict):
        # if self.isHidden():
            # self.setHidden(False)
            # self.raise_()
            # self.setWindowFlag(Qt.WindowStaysOnTopHint,True)
        # if not self.isActiveWindow():
        #     self.activateWindow()
        self.resetPlayerContext()
        self.setWindowFlag(Qt.WindowStaysOnTopHint,True)
        self.show()
        self.setWindowFlag(Qt.WindowStaysOnTopHint,False)
        self.show()
            # self.raise_()
            # self.setWindowFlag(Qt.WindowStaysOnTopHint,False)
        
        if params["type"] == "video":
            await self.initVideoInfo(params)
            self.toPlayVideo(self.videoInfo.get_defult_cid())
        elif params["type"] == "episode":
            await self.initEpisodeInfo(params)
            self.toPlayEpisode(self.episodeInfo.get_defult_epid())

    def resetPlayerContext(self):
        self.ExtendButton.setText("展开")
        self.DescriptionBox.setHidden(True)
        self.EpisodeBox.setHidden(True)

    def showEpisodeBox(self,episodeList):
        stringListModel=QStringListModel()
        stringListModel.setStringList(episodeList)
        self.EpisodeListBox.setModel(stringListModel)
        self.EpisodeBox.setHidden(False)

    @asyncSlot(QModelIndex)
    async def selectEpisode(self,index:QModelIndex):
        if self.currentPlayType == "episode":
            epid = self.indexToEpid[index.row()]
            await self.toPlayEpisode(epid)
        elif self.currentPlayType =="video":
            cid = self.indexToCid[index.row()]
            await self.toPlayVideo(cid)
        

    @asyncSlot(dict)
    async def initEpisodeInfo(self,params:dict):
        LOGGER.debug(f"episode info:\n{params}")
        media_id = params["data"]['media_id']
        season_id = params["data"]['season_id']
        # episode_id = params["data"]['episode_id']
        credential=params['credential']

        self.episodeInfo.init(media_id=media_id,ssid=season_id,credential=credential)
        await self.episodeInfo.requestInfo(media_id=media_id,
                                        ssid=season_id,
                                        credential=credential)
        self.loadEpisodeInfo(self.episodeInfo.info)

    def loadEpisodeInfo(self,info:dict):
        self.TitleBox.setText(info["title"])
        self.PlayInfoBox.setText(info["playInfo"])
        self.VideoIdBox.setText(str(info["id"]))
        self.DescriptionBox.setText(info["description"])
        self.currentPlayType = info["type"]
        self.indexToEpid ={}
        episodeList = []
        epids=info["epids"]
        LOGGER.debug(f"epid length: {len(epids)}")
        for index in range(len(epids)):
            title =epids[index]["title"]
            episodeList.append(title)
            self.indexToEpid[index] = epids[index]["epid"]
        self.showEpisodeBox(episodeList)




    @asyncSlot(dict)
    async def initVideoInfo(self,params:dict):
        LOGGER.debug(f"video info:\n{params}")
        aid = params["data"]['aid']
        bvid = params["data"]['bvid']
        credential=params['credential']
        # cid = params["data"]['cid']

        self.videoInfo.init(aid=aid,bvid=bvid,credential=credential)
        await self.videoInfo.requestInfo(bvid=bvid,
                                        aid=aid,
                                        credential=credential)
        self.loadVideoInfo(self.videoInfo.info)

    def loadVideoInfo(self,info:dict):
        self.TitleBox.setText(info["title"])
        self.PlayInfoBox.setText(info["playInfo"])
        self.VideoIdBox.setText(str(info["id"]))
        self.DescriptionBox.setText(info["description"])
        self.currentPlayType = info["type"]
        self.indexToCid ={}
        cids = info["cids"]
        LOGGER.debug(f"cid length: {len(cids)}")
        if len(cids)>1:
            episodeList = []
            for index in range(len(cids)):
                title =cids[index]["title"]
                episodeList.append(title)
                self.indexToCid[index] = cids[index]["cid"]
            self.showEpisodeBox(episodeList)

    @asyncSlot(int)
    async def toPlayEpisode(self,epid:int):
        self.currentMediaInfoDict = await self.episodeInfo.createMediaInfo(epid=epid)
        id = self.currentMediaInfoDict["defult"]
        video_url=self.currentMediaInfoDict["media_info"][id][0].video_url
        LOGGER.debug(f"episode link:\n{video_url}")
        self.play(self.currentMediaInfoDict["media_info"][id][0])

    @asyncSlot(int)
    async def toPlayVideo(self,cid:int):
        self.currentMediaInfoDict = await self.videoInfo.createMediaInfo(cid=cid)
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
            
        