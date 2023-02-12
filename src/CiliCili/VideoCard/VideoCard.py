from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qasync import asyncSlot
from ..VideoInfo.VideoInfo import VideoInfo
from ..ui.VideoCard_UI import Ui_VideoCard
import aiohttp


class VideoCard(QWidget,Ui_VideoCard):

    aid=None
    bvid=None
    cid=None
    uri=None
    pic=None
    title=None
    duration=None
    pubdate=None
    owner=None
    stat=None
    is_followed=None
    rcmd_reason=None
    credential = None

    load_info_signal = pyqtSignal()

    to_play_signal = pyqtSignal(dict)

    def __init__(self,parent=None):
        super(VideoCard, self).__init__(parent=parent)
        self.setupUi(self)
        self.load_info_signal.connect(self.loadInfo)
        # self.VideoCover.click.connect(self.toPlay)
        # self.VideoTitle.click.connect(self.toPlay)
        # self.VideoAuthor.clicked.connect(self.toPlay)
        # self.PlayInfo.clicked.connect(self.toPlay)
        self.VideoCover.installEventFilter(self)
        self.VideoTitle.installEventFilter(self)
        self.VideoAuthor.installEventFilter(self)
        self.PlayInfo.installEventFilter(self)


    def eventFilter(self, obj: 'QObject', e: 'QEvent') -> bool:
        event_type = e.type()
        if obj in [self.VideoCover,self.VideoTitle,self.VideoAuthor,self.PlayInfo]:
            if event_type == QEvent.Type.MouseButtonRelease:
                if e.button() == Qt.MouseButton.LeftButton:
                    self.toPlay()
                    return True

        return super().eventFilter(obj, e)

    @asyncSlot()
    async def toPlay(self):
        d= {
            "aid":self.aid,
            "bvid":self.bvid,
            "cid":self.cid,
            "title":self.title,
            "credential":self.credential
        }

        # videoInfo=VideoInfo(self.bvid,self.aid)
        # await videoInfo.requestData()
        # print(videoInfo.info)
        self.to_play_signal.emit(d)

    @asyncSlot()
    async def loadInfo(self):
        # print("loadInfo:",str(self.title))
        self.VideoTitle.setText(str(self.title))
        self.PlayInfo.setText(str(self.bvid))
        await self.setCover(self.pic)
        
        
    @asyncSlot()
    async def setCover(self,uri):
        # aiohttp.request(uri)
        # 建立会话session
        conn = aiohttp.TCPConnector(ssl=False)  # 防止ssl报错
        async with aiohttp.ClientSession(connector=conn) as session:
            content = await session.get(uri)
            img = await content.read()
            qpixmap = QPixmap()
            qpixmap.loadFromData(img)
            # img.scaled(self.VideoCover.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.VideoCover.setScaledContents(True)
            self.VideoCover.setPixmap(qpixmap)
