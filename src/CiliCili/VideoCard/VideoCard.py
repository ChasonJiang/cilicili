from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qasync import asyncSlot
from ..VideoInfo.VideoInfo import VideoInfo
from ..ui.VideoCard_UI import Ui_VideoCard
import aiohttp


class VideoCard(QWidget,Ui_VideoCard):

    pic=None
    title=None
    authorInfo=None
    dateInfo=None
    type = None
    data = None
    credential = None

    """
        type is a string, "video" or "episode" 

        data is a dictionary
        like this:
        {
            "aid":,
            "bvid":,
            "cid":,
            "title":,
            "description":,
            "owner":{
                "name":,
                "mid":,
                "face":,
            }
        }
        or
        {
            "title":,
            "media_id":,
            "season_id":,
            "description":,
        }

    """


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
        # self.setMouseTracking(False)


    def eventFilter(self, obj: 'QObject', e: 'QEvent') -> bool:
        event_type = e.type()
        if obj in [self.VideoCover,self.VideoTitle,self.VideoAuthor,self.PlayInfo]:
            if event_type == QEvent.Type.MouseButtonRelease:
                if e.button() == Qt.MouseButton.LeftButton:
                    self.toPlay()
                    return True

        return super().eventFilter(obj, e)


    @asyncSlot(str)
    async def toPlay(self,):
        d={
            "type":self.type,
            "data":self.data,
            "credential":self.credential
        }
        # videoInfo=VideoInfo(self.bvid,self.aid)
        # await videoInfo.requestData()
        # print(videoInfo.info)
        self.to_play_signal.emit(d)

    @asyncSlot()
    async def loadInfo(self):
        # print("loadInfo:",str(self.title))
        self.VideoTitle.setText(self.title)
        self.VideoAuthor.setText(self.authorInfo)
        self.PlayInfo.setText(self.dateInfo)
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
            qpixmap.scaled(self.VideoCover.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode .SmoothTransformation)
            self.VideoCover.setScaledContents(True)
            self.VideoCover.setPixmap(qpixmap)
