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
        self.srContext:SRContext = srContext
        self.CiliCiliPlayer = CiliCiliPlayer(self,srContext)
        self.setupUi(self,self.CiliCiliPlayer)
        self.switch_full_screen_signal.connect(self.switchFullScreen)

        # 与MianWindow建立通信
        self.node = QRemoteObjectNode(parent=self)
        self.node.connectToNode(QUrl("local:MainWindow"))

        self.host = self.node.acquireDynamic('MainWindow')
        self.host.initialized.connect(self.onInitialized)

        self.videoInfo:VideoInfo = VideoInfo()
        self.curr_cid = None
        self.currentMediaInfoDict = None


    def onInitialized(self):
        self.host.to_play_signal.connect(self.initVideoInfo)

    

    @asyncSlot(dict)
    async def initVideoInfo(self,params:dict):
        print(params)
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

    # @asyncSlot()
    # async def receiveCmd(self):
    #     while True:
            
        