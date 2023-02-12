import functools
import sys
import asyncio
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QEventLoop as QtEventLoop
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .VideoCard.VideoCardParser import VideoCardParser
from .VideoCard.VideoCard import VideoCard
from .FlowLayout import FlowLayout
from bilibili_api import homepage

from .ui.MainWindow_UI import Ui_MainWindow
import qasync
from qasync import QThreadExecutor, asyncSlot, asyncClose,QEventLoop
from PyQt5.QtRemoteObjects import QRemoteObjectHost

class MainWindow(QWidget,Ui_MainWindow):
    call_func_signal = pyqtSignal()
    load_card_signal = pyqtSignal(list)
    load_video_card_signal = pyqtSignal(list)
    to_play_signal = pyqtSignal(dict)
    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.setWindowFlag(Qt.FramelessWindowHint, False)
        self.setupUi(self)
        self.flowLayout = FlowLayout(self.scrollAreaContents,30,20,20)
        self.loop = asyncio.get_event_loop()
        self.RefreshButton.clicked.connect(self.refresh)
        self.videoCardParser = VideoCardParser()
        self.host = QRemoteObjectHost(QUrl("local:MainWindow"),parent=self)
        self.host.enableRemoting(self, 'MainWindow')

        # @asyncSlot()
        # async def fun():
        #     self.refresh()
        # asyncio.create_task(fun())
        # self.refresh()


    @asyncSlot()
    async def refresh(self):
        self.flowLayout.clear()
        self.request()


    @asyncSlot()
    async def request(self):
        # try:
            data = await homepage.get_videos()
            videoCardList = self.videoCardParser.parse(data,self.scrollAreaContents)
            
            for item in videoCardList:
                item.to_play_signal.connect(self.toPlay)
                self.flowLayout.addWidget(item)
                item.load_info_signal.emit()
  

    def toPlay(self,data:dict):
        self.to_play_signal.emit(data)
        # except Exception as e:
        #     print("请求异常! code segment: MainWindow.request")
            # return





def m():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    mainWindow = MainWindow()
    mainWindow.show()
    # mainWindow.call_func_signal.emit()
    with loop:
        loop.run_forever()
        

async def main():
    def close_future(future, loop):
        loop.call_later(10, future.cancel)
        future.cancel()

    loop = asyncio.get_event_loop()
    future = asyncio.Future()

    app = QApplication.instance()
    if hasattr(app, "aboutToQuit"):
        getattr(app, "aboutToQuit").connect(
            functools.partial(close_future, future, loop)
        )

    mainWindow = MainWindow()
    mainWindow.show()

    await future
    return True

if __name__ == "__main__":
    try:
    # qasync.run(master())
    # m()
        qasync.run(main())
    except asyncio.exceptions.CancelledError:
        sys.exit(0)
