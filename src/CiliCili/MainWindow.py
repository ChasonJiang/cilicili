import functools
import logging
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
from bilibili_api import homepage,search

from .ui.MainWindow_UI import Ui_MainWindow
import qasync
from qasync import QThreadExecutor, asyncSlot, asyncClose,QEventLoop
from PyQt5.QtRemoteObjects import QRemoteObjectHost
LOGGER=logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class MainWindow(QWidget,Ui_MainWindow):
    call_func_signal = pyqtSignal()
    load_card_signal = pyqtSignal(list)
    load_video_card_signal = pyqtSignal(list)
    to_play_signal = pyqtSignal(dict)
    close_palyer_window_signal = pyqtSignal()
    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent=parent)
        LOGGER.debug("init MainWindow")
        # self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        # self.setAttribute(Qt.WA_TranslucentBackground,True)
        # self.setWindowOpacity(0)
        self.loop = asyncio.get_event_loop()
        self.setupUi(self)
        self.initContainer()
        self.initDragAndResize()
        self.initRemoteObjects()
        self.initConnection()
        
        self.initSearchContext()
        self.videoCardParser = VideoCardParser()

    def initRemoteObjects(self):
        self.host = QRemoteObjectHost(QUrl("local:MainWindow"),parent=self)
        self.host.enableRemoting(self, 'MainWindow')
        LOGGER.debug("RemoteObjects inited")

    def initConnection(self):
        self.scrollBar.valueChanged.connect(self.load)
        self.RefreshButton.clicked.connect(self.refresh)
        self.CloseButton.clicked.connect(self.close)
        self.MinButton.clicked.connect(self.showMinimized)
        self.MaxButton.clicked.connect(self.showMaximized)
        self.SearchBox.returnPressed.connect(self.search)
        self.SearchButton.clicked.connect(lambda :self.switchPage(self.searchPage))
        self.HomeButton.clicked.connect(lambda :self.switchPage(self.homePage))
        def func():
            index = 0
            try:
                index = self.pageIndexStack.pop()
            except:
                pass
            finally:
                self.switchPage(self.pageList[index],recode=True)
        self.BackButton.clicked.connect(func)
        LOGGER.debug("RemoteObjects inited")

    def initSearchContext(self):
        self.search_page = 1
        self.search_keyword = None
        self.search_max_page = 1
        LOGGER.debug("SearchContext inited")

    def initContainer(self):
        self.scrollBar = QScrollBar()
        self.scrollArea.setVerticalScrollBar(self.scrollBar)
        self.stackLayout = QStackedLayout()
        self.stackLayout.setContentsMargins(0,0,0,0)
        self.stackLayout.setSpacing(0)
        self.scrollAreaContents.setLayout(self.stackLayout)
        self.pageList = []

        self.homePage = QWidget()
        self.homePage.setGeometry(QRect(0, 0, 1534, 830))
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.homePage.sizePolicy().hasHeightForWidth())
        self.homePage.setSizePolicy(sizePolicy)
        self.homePage.setStyleSheet("#homePage{\n"
"background-color:rgba(0,0,0,0);\n"
"}")
        self.homePage.setObjectName("homePage")
        self.pageList.append(self.homePage)

        self.searchPage = QWidget()
        self.searchPage.setGeometry(QRect(0, 0, 1534, 830))
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.searchPage.sizePolicy().hasHeightForWidth())
        self.searchPage.setSizePolicy(sizePolicy)
        self.searchPage.setStyleSheet("#searchPage{\n"
"background-color:rgba(0,0,0,0);\n"
"}")
        self.searchPage.setObjectName("searchPage")
        self.pageList.append(self.searchPage)

        self.pageIndexDict = {}
        #添加page并记录page的flowLayout
        self.pageFlowLayoutList = []
        for index in range(len(self.pageList)):
            self.pageIndexDict[self.pageList[index]]=index
            self.stackLayout.insertWidget(index, self.pageList[index])
            self.pageFlowLayoutList.append(FlowLayout(self.pageList[index],30,20,30))

        #记录用户选择page的index
        self.pageIndexStack = []
        #设置homePage为当前页面
        self.currentPageIndex = 0
        self.pageIndexStack.append(0)
        self.stackLayout.setCurrentIndex(0)

        LOGGER.debug("Container inited")
    

    def switchPage(self,w:QWidget,recode:bool=False):
        if recode:
            self.pageIndexStack.append(self.currentPageIndex)
        self.currentPageIndex = self.pageIndexDict[w]
        LOGGER.debug(f"switch page to {self.currentPageIndex}")
        self.stackLayout.setCurrentIndex(self.currentPageIndex)


    @asyncSlot()
    async def refresh(self):
        flowLayout =self.pageFlowLayoutList[self.currentPageIndex]
        flowLayout.clear()
        data = await self.request()
        if data is None:
            return
        self.addToContainer(data)
    
    @asyncSlot()
    async def search(self):
        keyword = self.SearchBox.text()
        if keyword is None or len(keyword)==0:
            return
        self.initSearchContext()
        flowLayout =self.pageFlowLayoutList[self.currentPageIndex]
        flowLayout.clear()
        self.switchPage(self.searchPage)
        self.search_keyword = keyword
        LOGGER.debug(f"searching {self.search_keyword}")
        data = await self.request()
        if data is None:
            return
        self.addToContainer(data)

    @asyncSlot()
    async def load(self):
        if self.scrollBar.maximum() == self.scrollBar.value():
            data = await self.request()
            if data is None:
                return
            self.addToContainer(data)


    @asyncSlot()
    async def request(self,):
        LOGGER.debug("request video info")
        # try:
        data = None
        if self.stackLayout.currentWidget() == self.homePage:
            d = await homepage.get_videos()
            data = {
                "from":"homepage",
                "data":d
            }
        elif self.stackLayout.currentWidget() == self.searchPage:
            if not self.search_page>self.search_max_page and self.search_keyword is not None:
                d = await search.search(keyword=self.search_keyword,page=self.search_page)
                self.search_max_page = int(d["numPages"])
                data = {
                    "from":"search",
                    "data":d["result"],
                    "page":self.search_page
                }
                self.search_page+=1
        return data
            
    def addToContainer(self,data:dict):
            videoCardList = self.videoCardParser.parse(data,self.pageList[self.currentPageIndex])
            for item in videoCardList:
                flowLayout:FlowLayout = self.pageFlowLayoutList[self.currentPageIndex]
                item.to_play_signal.connect(self.toPlay)
                flowLayout.addWidget(item)
                item.load_info_signal.emit()
  

    def toPlay(self,data:dict):
        self.to_play_signal.emit(data)
        # except Exception as e:
        #     print("请求异常! code segment: MainWindow.request")
            # return


    def closeEvent(self, a0: QCloseEvent) -> None:
        self.close_palyer_window_signal.emit()
        return super().closeEvent(a0)


    def initDragAndResize(self):
        self.setMouseTracking(True)
        self.ContainerWindow.setMouseTracking(True)
        self.TopBar.setMouseTracking(True)
        self.LeftBar.setMouseTracking(True)
        self.MainContainer.setMouseTracking(True)
        self.Container.setMouseTracking(True)
        self.scrollArea.setMouseTracking(True)
        self.scrollAreaContents.setMouseTracking(True)
        self.homePage.setMouseTracking(True)
        self.searchPage.setMouseTracking(True)
        self.TopBar.installEventFilter(self)
        self.LeftBar.installEventFilter(self)
        self.MainContainer.installEventFilter(self)
        self.Container.installEventFilter(self)
        self.scrollArea.installEventFilter(self)
        self.scrollAreaContents.installEventFilter(self)
        self.homePage.installEventFilter(self)
        self.searchPage.installEventFilter(self)
        # self.initDrag()
        self.mouseTriggerReset()
        self.relativePos = None
        self.resizeBorderThreshold = 4

    def eventFilter(self, w: QObject, e: QEvent) -> bool:
        if w in [self.TopBar, self.LeftBar, self.Container, self.scrollArea, self.scrollAreaContents,self.homePage, self.searchPage]:
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
