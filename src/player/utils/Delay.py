import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import time


def delay_ns(t:float):
    start_time = time.perf_counter()
    while (time.perf_counter() - start_time) < t:
        continue

class Delay():
    def __init__(self, targetDelayTime:float):
        self.targetDelayTime = targetDelayTime
        self.averageError = 0
        self.standardDeviation = 0
        self.oldAverageError = 0
        self.oldStdOfTargetDelayTime = 0


def delay_ms(t:float):
    eventLoop=QEventLoop()
    QTimer.singleShot(t,eventLoop.quit)
    eventLoop.exec()



if __name__ == '__main__':
    # app = QApplication(sys.argv)
    # while True:
    #     # start_time = time.perf_counter()
    #     # delay_ns(0.003)
    #     # time.sleep(0.020)
    #     # QThread.usleep(100)
    #     delay_ms(10)
    #     # print(time.perf_counter()-start_time)

    # exit(app.exec_())
    while True:
        start_time = time.time()
        time.sleep(1)
        print(time.time()-start_time)