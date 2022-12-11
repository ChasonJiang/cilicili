import sys
from time import sleep, time
import cv2
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from threading import Thread
import ffmpeg
import numpy as np


class DisplayLayer(QWidget):
    def __init__(self,parent=None):
        super(DisplayLayer, self).__init__(parent=parent)
        self.painter = QPainter()
        # img = cv2.imread("assets\\8k.jpg")
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # self.curr_frame = img
        self.curr_frame=np.zeros((1,1,3),dtype=np.uint8)

        self.setupUi()

    def setupUi(self,):
        # 隐藏窗口边框
        # self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setWindowTitle("DisdlayLayer")
        self.setObjectName("DisdlayLayer")
        

        # 设置外边距
        self.setContentsMargins(0,0,0,0)
        # self.setGeometry(0,0,600,600)

    def paintEvent(self,event):
        height, width, channel = self.curr_frame.shape
        bytesPerLine = channel * width
        qImg = QImage(self.curr_frame.data, width, height, bytesPerLine, QImage.Format_RGB888)

        self.painter.begin(self)
        self.painter.setRenderHint(QPainter.Antialiasing, True)
        self.painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setDisplayMode()
        self.painter.drawImage(QRect(0, 0, width, height), qImg)
        self.painter.end()
        super().paintEvent(event)

    def setDisplayMode(self, aspectRatio=-1, mode="auto"):
        """
            Args:
                aspectRatio(int): aspectRatio to be displayed. The default value is - 1, which means the aspect ratio of the frame is used
                mode(str): mode to be displayed. 
        """
        height, width, _ = self.curr_frame.shape
        # print(self.curr_frame.shape)
        if aspectRatio == -1:
            aspectRatio = 1.0 * width / height
        if mode == "auto":
            self.painter.setWindow(0, 0, width, height)
            v_h = 0
            v_w = 0
            if aspectRatio*self.height()>self.width():
                v_h = round(self.width() / aspectRatio)
                v_w = self.width()
            else:
                v_h = self.height()
                v_w = round(self.height() * aspectRatio)
            v_x = round((self.width() - v_w) / 2.0)
            v_y = round((self.height() - v_h) / 2.0)

            self.painter.setViewport(v_x, v_y, v_w, v_h)



    def update(self, img:np.ndarray):
        """
            Args:
                img: np.ndarray, np.uint8, (height, width, channel), RGB image.
        """
        # assert isinstance(img,np.ndarray)
        self.curr_frame = img
        super().update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    displayLayer = DisplayLayer()
    displayLayer.show()
    sys.exit(app.exec_())
