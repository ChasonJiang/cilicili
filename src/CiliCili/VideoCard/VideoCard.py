from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qasync import asyncSlot
from ui.VideoCard_UI import Ui_VideoCard
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

    load_info_pyqt = pyqtSignal()

    to_play_pyqt = pyqtSignal(dict)

    def __init__(self,parent=None):
        super(VideoCard, self).__init__(parent=parent)
        self.setupUi(self)
        self.load_info_pyqt.connect(self.loadInfo)
        self.VideoCover.clicked.connect(self.toPlay)
        self.VideoTitle.clicked.connect(self.toPlay)
        self.VideoAuthor.clicked.connect(self.toPlay)
        self.PlayInfo.clicked.connect(self.toPlay)

    @asyncSlot()
    async def toPlay(self):
        d= {
            "aid":self.aid,
            "bvid":self.bvid,
            "cid":self.cid,
            "title":self.title,
        }


        self.to_play_pyqt.emit(d)

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
