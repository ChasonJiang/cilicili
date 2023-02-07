import functools
import sys
import asyncio
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QEventLoop as QtEventLoop
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from VideoCard.VideoCardParser import VideoCardParser
from VideoCard.VideoCard import VideoCard
from FlowLayout import FlowLayout
from bilibili_api import homepage

from ui.MainWindow_UI import Ui_MainWindow
import qasync
from qasync import QThreadExecutor, asyncSlot, asyncClose,QEventLoop


class MainWindow(QWidget,Ui_MainWindow):
    call_func_signal = pyqtSignal()
    load_card_signal = pyqtSignal(list)
    load_video_card_signal = pyqtSignal(list)
    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.setWindowFlag(Qt.FramelessWindowHint, False)
        self.setupUi(self)
        self.flowLayout = FlowLayout(self.scrollAreaContents,30,20,20)
        self.loop = asyncio.get_event_loop()
        self.RefreshButton.clicked.connect(self.refresh)
        self.videoCardParser = VideoCardParser()

    @asyncSlot()
    async def refresh(self):
        self.flowLayout.clear()
        self.request()


    @asyncSlot()
    async def func(self):
        asyncio.run(self.call_fun())
        await asyncio.sleep(4)

    @asyncSlot()
    async def request(self):
        try:
            data = await homepage.get_videos()
            videoCardList = self.videoCardParser.parse(data,self.scrollAreaContents)
            
            for item in videoCardList:
                self.flowLayout.addWidget(item)
                item.load_info_pyqt.emit()
  
        except Exception as e:
            print("请求异常! code segment: MainWindow.request")
            # return





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


def m():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    mainWindow = MainWindow()
    mainWindow.show()
    # mainWindow.call_func_signal.emit()
    with loop:
        loop.run_forever()
        

if __name__ == "__main__":
    try:
    # qasync.run(master())
    # m()
        qasync.run(main())
    except asyncio.exceptions.CancelledError:
        sys.exit(0)
