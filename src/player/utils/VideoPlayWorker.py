import logging
from queue import Queue
from time import perf_counter, sleep
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Tools.Delay import delay_ns
from player.utils.PlayClock import PlayClock
from ..DisplayLayer import DisplayLayer
# logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO) # DEBUG
LOGGER=logging.getLogger()


class VideoPlayWorker(QObject):
    wait_buffer_signal = pyqtSignal(str)
    pause_signal = pyqtSignal()
    resume_signal = pyqtSignal()
    quit_signal = pyqtSignal(bool)
    set_frame_rate = pyqtSignal(int)
    update_buffer_queue = pyqtSignal(Queue)
    
    def __init__(self,display_device, buffer_queue, play_clock):
        super(VideoPlayWorker, self).__init__()
        LOGGER.info("init VideoPlayWorker")
        assert isinstance(display_device,DisplayLayer)
        assert isinstance(buffer_queue,Queue)
        assert isinstance(play_clock,PlayClock)
        self.display_device=display_device
        self.buffer_queue = buffer_queue
        self.play_clock = play_clock
        self._isPause = False
        self._isQuit = False
        self.forced_quit = False
        self.cond = QWaitCondition()
        self.mutex = QMutex()
        self.curr_frame_rate = 30
        self.resume_signal.connect(self.resume)
        self.pause_signal.connect(self.pause)
        self.set_frame_rate.connect(self.setFrameRate)
        self.update_buffer_queue.connect(self.updateBufferQueue)
        self.delay_constant = 0
        self.max_sync_threshold = 100 # ms
        self.min_sync_threshold = -100 # ms
        self.nosync_threshold = 10
        self.frame_last_delay = 0.0
        self.frame_last_pts =  0.0
        self.drop_frame_flag = False
        self.drop_frame_counter = 0
        self.frame_counter = 0
        self.frame_timer = 0
        self.min_refresh_time = 8

    def setFrameRate(self,frame_rate:int):
        self.curr_frame_rate = frame_rate
        self.delay_constant = 1000.0/self.curr_frame_rate
        # self.frame_last_delay = self.delay_constant
        # LOGGER.debug(self.frame_last_delay)

    def updateBufferQueue(self,buffer_queue):
        self.mutex.lock()
        self.buffer_queue = buffer_queue
        self.mutex.unlock()

    def pause(self):
        LOGGER.debug("pause VideoPlayWorker")
        self._isPause = True

    def resume(self):
        self.mutex.lock()
        LOGGER.debug("resume VideoPlayWorker")
        self._isPause = False
        self.cond.wakeAll()
        self.mutex.unlock()

    def quit(self):
        self._isQuit = True

    def forcedQuit(self):
        self.forced_quit = True

    def delay_ms(self, t:float):
        eventLoop=QEventLoop()
        QTimer.singleShot(t,eventLoop.quit)
        eventLoop.exec()
        
    def play(self):
        # assert self.curr_frame_rate is not None
        # print("thread id of VideoPlayWorker is {}".format(QThread.currentThreadId()))
        while True:
            if self._isQuit and self.buffer_queue.empty():
                break
            if self.forced_quit:
                # 防止decoder因缓冲队满而阻塞,导致无法正常退出
                if self.buffer_queue.full():
                    self.buffer_queue.get_nowait()
                    self.buffer_queue.get_nowait()
                break

            self.mutex.lock()
            if self.buffer_queue.empty():
                self.wait_buffer_signal.emit("display_device")
                LOGGER.debug("Video frame queue is empty")
                self._isPause = True

            if self._isPause:
                LOGGER.debug("VideoPlayWorker paused")
                # 使用QWaitCondition阻塞时，os调用wait_block的“瞬间”会释放mutex
                self.cond.wait(self.mutex)

                if self._isQuit and self.buffer_queue.empty():
                    break
                if self.forced_quit:
                    # 防止decoder因缓冲队满而阻塞,导致无法正常退出
                    if self.buffer_queue.full():
                        self.buffer_queue.get_nowait()
                        self.buffer_queue.get_nowait()
                    break


            buffer = self.buffer_queue.get(block=True)
            self.frame_counter += 1

            curr_pts = buffer["pts"]
            delay = curr_pts - self.frame_last_pts
            if delay<0 or delay >1000.0:
                delay = self.frame_last_delay
            ref_clock = self.play_clock.getClock()
            diff = curr_pts - ref_clock # diff<0, video slow; diff>0, video fast
            sync_threshold = max(self.min_sync_threshold,min(delay, self.max_sync_threshold))

            # LOGGER.debug("curr_pts: {:.2f} | ref_clock: {:.2f} | diff: {:.2f} | delay: {:.2f}".format(curr_pts, ref_clock, diff, delay))

            if (abs(diff) > self.nosync_threshold):
                # video slow
                if (diff <= -sync_threshold):
                    delay = max(0, delay + diff)
                if (diff < -1000.0):
                    self.drop_frame_flag = True
                    LOGGER.warning("The video is slow, and the frame will be discarded")
                # video fast
                elif (diff >= sync_threshold and delay > self.delay_constant):
                    delay += diff
                elif (diff >= sync_threshold):
                    delay *= 2

            self.frame_last_delay = delay
            self.frame_last_pts = curr_pts

            curr_time = time.perf_counter() *1000
            if self.frame_timer == 0:
                self.frame_timer = curr_time
            
            actual_delay = self.frame_timer + delay - curr_time


            if actual_delay < self.min_refresh_time:
                actual_delay = self.min_refresh_time
            # LOGGER.debug("video delay {} ms".format(delay))
            # LOGGER.debug("video actual_delay {} ms".format(actual_delay))
            if not self.drop_frame_flag:
                self.delay_ms(actual_delay)
                self.display_device.update(buffer["data"])
            else:
                self.drop_frame_counter+=1
                self.drop_frame_flag = False
            self.frame_timer = time.perf_counter()*1000

            self.mutex.unlock()

        LOGGER.debug("The frame loss rate of this video is {:.2f} %".format((1.0*self.drop_frame_counter/self.frame_counter)*100))
        LOGGER.debug("VideoPlayWorker quit")
        self.quit_signal.emit(True)
