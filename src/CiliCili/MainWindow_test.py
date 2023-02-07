import functools
import sys
import asyncio
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from GLayout import GLayout
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
        # self.content = self.scrollAreaContents
        self.flowLayout = GLayout(None,40,20,20)
        self.scrollArea.setWidget(self.flowLayout)
        # self.videoCard = VideoCard(self.scrollAreaContents)
        # self.flowLayout.addWidget(self.videoCard)
        self.loop = asyncio.get_event_loop()
        # videoCard = VideoCard(self.flowLayout)
        # self.flowLayout.addWidget(VideoCard())
        # for i in range(20):
        #     print(f"Setting: {i}")
        #     w=VideoCard(self.flowLayout)
        #     w.VideoTitle.setText("sdfgdsfg")
        #     self.flowLayout.addWidget(w)

        
        # self.call_func_signal.connect(self.r)
        self.RefreshButton.clicked.connect(self.refresh)
        self.videoCardParser = VideoCardParser()
        # self.load_card_signal.connect(self.loadCard)
        # self.load_video_card_signal.connect(self.loadVideoCard)
        # self.videoCardList=[VideoCard(self.scrollAreaContents)for i in range(30)]
        
        # self.r()

    def refresh(self):
        self.flowLayout.addWidget(VideoCard())

    @asyncSlot()
    async def func(self):
        asyncio.run(self.call_fun())
        await asyncio.sleep(4)

    @asyncSlot()
    async def request(self):
        data= await homepage.get_videos()
        items=data["item"]
        # videoCardList = self.videoCardParser.parse(items,self.videoCardList)
        # self.load_card_signal.emit(videoCardList)
        for item in items:
            # asyncio.create_task(item.loadInfo())
            videoCard=self.videoCardParser.parser(item,VideoCard())
            print(videoCard.bvid)
            await videoCard.loadInfo()
            # videoCard.setupUi(videoCard)
            videoCard.resize(QSize(242,222))
            videoCard.setFixedSize(QSize(242,222))
            videoCard.setMinimumSize(QSize(242,222))
            videoCard.VideoTitle.setText("asdf")
            # print(videoCard.sizeHint())
            self.flowLayout.addWidget(videoCard)
        self.flowLayout.updateGeometry()

    def loadCard(self,videoCardList):
    #    for item in videoCardList:
    #         # asyncio.create_task(item.loadInfo())
    #         print(item.bvid)
    #         # item.loadInfo()
    #         self.flowLayout.addWidget(item)
        self.load_video_card_signal.emit(videoCardList)

    def loadVideoCard(self,videoCardList):
        for item in videoCardList:
                # asyncio.create_task(item.loadInfo())
                print(item.bvid)
                # item.loadInfo()
                self.flowLayout.addWidget(item)

        # self.update()
    # def r(self):
    #     self.request()
    def r(self):
        for item in self.videoCardList:
            # print(f"Setting: {i}")
            self.flowLayout.addWidget(item)
        self.scrollAreaContents.setLayout(self.flowLayout)
        # self.update()
        
    @asyncSlot()
    async def call_fun(self):
        # fun1()
        # fun2()
        # cmd = asyncio.create_task([fun1(self.loop),fun2(self.loop)])
        # asyncio.run(cmd)
        # asyncio.ensure_future(fun1, loop=self.loop)
        # task=asyncio.create_task(fun1())
        # pass
        await asyncio.sleep(2)
        print("asdf")
        # task.result()


async def fun1():
    # await asyncio.sleep(10,)
    # print("fun1 called")
    while True:
        print("fun1 running")
        await asyncio.sleep(0.01)

async def fun2(loop=None):
    await asyncio.sleep(8,loop=loop)
    print("fun2 called")

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
    # asyncio.sleep(12)
    mainWindow = MainWindow()
    mainWindow.show()

    # mainWindow.call_fun()
    # mainWindow.fun1()
    # mainWindow.fun2()
    await future
    return True

async def master():
    mainWindow = MainWindow()
    mainWindow.show()

    loop = asyncio.get_running_loop()
    with QThreadExecutor(1) as exec:
        await loop.run_in_executor(exec, functools.partial(mainWindow), loop)


def m():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    mainWindow = MainWindow()
    mainWindow.show()
    mainWindow.refresh()
    mainWindow.refresh()
    mainWindow.update()
    # mainWindow.call_func_signal.emit()
    with loop:
        loop.run_forever()
        

if __name__ == "__main__":
    # try:
    # qasync.run(master())
    m()
    # except asyncio.exceptions.CancelledError:
    #     sys.exit(0)


# async def main():
#     app = QApplication(sys.argv)
#     mainWindow=MainWindow()
#     mainWindow.show()
#     mainWindow.fun1()
#     mainWindow.fun2()
#     sys.exit(app.exec_())



# if __name__ == "__main__":
#     asyncio.run(main())