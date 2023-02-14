import functools
import sys
import asyncio
from tkinter import W
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
    close_palyer_window_signal = pyqtSignal()
    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent=parent)
        # self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        # self.setAttribute(Qt.WA_TranslucentBackground,True)
        # self.setWindowOpacity(0)
        self.setupUi(self)
        self.scrollBar = QScrollBar()
        self.scrollArea.setVerticalScrollBar(self.scrollBar)
        self.flowLayout = FlowLayout(self.scrollAreaContents,30,20,20)
        self.loop = asyncio.get_event_loop()
        self.RefreshButton.clicked.connect(self.refresh)
        self.videoCardParser = VideoCardParser()
        self.host = QRemoteObjectHost(QUrl("local:MainWindow"),parent=self)
        self.host.enableRemoting(self, 'MainWindow')
        self.initDragAndResize()
        self.scrollBar.valueChanged.connect(self.load)

        self.CloseButton.clicked.connect(self.close)
        self.MinButton.clicked.connect(self.showMinimized)
        self.MaxButton.clicked.connect(self.showMaximized)

        # @asyncSlot()
        # async def fun():
        #     self.refresh()
        # asyncio.create_task(fun())
        # self.refresh()

    def initDragAndResize(self):
        self.setMouseTracking(True)
        self.ContainerWindow.setMouseTracking(True)
        self.TopBar.setMouseTracking(True)
        self.LeftBar.setMouseTracking(True)
        self.MainContainer.setMouseTracking(True)
        self.Container.setMouseTracking(True)
        self.scrollArea.setMouseTracking(True)
        self.scrollAreaContents.setMouseTracking(True)
        self.TopBar.installEventFilter(self)
        self.LeftBar.installEventFilter(self)
        self.MainContainer.installEventFilter(self)
        self.Container.installEventFilter(self)
        self.scrollArea.installEventFilter(self)
        self.scrollAreaContents.installEventFilter(self)
        # self.initDrag()
        self.mouseTriggerReset()
        self.relativePos = None
        self.resizeBorderThreshold = 4

    def eventFilter(self, w: QObject, e: QEvent) -> bool:
        if w in [self.TopBar, self.LeftBar, self.Container, self.scrollArea, self.scrollAreaContents]:
            e_type = e.type()
            if e_type == QEvent.Type.MouseButtonPress:
                if e.button() == Qt.LeftButton:
                    self.is_pressed = True
                    self.mousePressEvent(e)
                    return True
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
            elif e.windowPos().y()<=self.TopBar.height() and e.windowPos().x() >self.LeftBar.width():
                self.window_move = True
            self.relativePos = e.windowPos()
            self.absolutePos = e.globalPos()
            return e.accept()
        else:
            return super().mousePressEvent(e)

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        # print(e.windowPos())
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

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        self.mouseTriggerReset()
        # return super().mouseReleaseEvent(e)

        


    @asyncSlot()
    async def refresh(self):
        self.flowLayout.clear()
        self.request()

    @asyncSlot()
    async def load(self):
        if self.scrollBar.maximum() == self.scrollBar.value():
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


    def closeEvent(self, a0: QCloseEvent) -> None:
        self.close_palyer_window_signal.emit()
        return super().closeEvent(a0)





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
