import logging
from queue import Queue
from time import perf_counter, sleep
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Tools.Delay import delay_ns
from player.utils.PlayClock import PlayClock

from .AudioDevice import AudioDevice
# logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO) # DEBUG
LOGGER=logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class AudioPlayWorker(QObject):
    wait_buffer_signal = pyqtSignal(bool)
    pause_signal = pyqtSignal()
    resume_signal = pyqtSignal()
    quit_signal = pyqtSignal(bool)
    set_frame_rate = pyqtSignal(float)
    update_buffer_queue = pyqtSignal(Queue)

    def __init__(self,audio_device, buffer_queue, play_clock):
        super(AudioPlayWorker, self).__init__()
        LOGGER.info("init AudioPlayWorker")
        assert isinstance(audio_device,AudioDevice)
        assert isinstance(buffer_queue,Queue)
        assert isinstance(play_clock,PlayClock)
        self.audio_device=audio_device
        self.buffer_queue = buffer_queue
        self.play_clock = play_clock
        self._isPause = False
        self._isQuit = False
        self.forced_quit = False
        self.cond = QWaitCondition()
        self.mutex = QMutex()
        self.resume_signal.connect(self.resume)
        self.pause_signal.connect(self.pause)
        self.set_frame_rate.connect(self.setFrameRate)
        self.update_buffer_queue.connect(self.updateBufferQueue)
        self.curr_frame_rate = 30

    def setFrameRate(self,frame_rate:int):
        self.curr_frame_rate = frame_rate

    def updateBufferQueue(self,buffer_queue):
        self.mutex.lock()
        self.buffer_queue = buffer_queue
        self.mutex.unlock()

    def pause(self):
        LOGGER.debug("pause AudioPlayWorker")
        self._isPause = True

    def resume(self):
        self.mutex.lock()
        LOGGER.debug("resume AudioPlayWorker")
        self._isPause = False
        self.cond.wakeAll()
        self.mutex.unlock()

    def updateSyncTime(self,sync_time:int):
        self.sync_time = sync_time
        
    def quit(self):
        self._isQuit = True
        self.resume()

    def forcedQuit(self):
        self.forced_quit = True
        self.resume()

    def delay_ms(self, t:int):
        eventLoop=QEventLoop()
        QTimer.singleShot(t,eventLoop.quit)
        eventLoop.exec()


    def play(self):
        # self.delay_ms(10)
        # assert self.curr_frame_rate is not None
        is_block = False
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
                self.wait_buffer_signal.emit(True)
                LOGGER.debug("Audio frame queue is empty")
                self._isPause = True

            if self._isPause:
                LOGGER.debug("AudioPlayWorker paused")
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

            # self.delay_ms(60)
            # sleep(0.1)
            self.play_clock.updateClock(buffer["pts"])
            self.audio_device.update(buffer["data"])
            

            self.mutex.unlock()

        LOGGER.debug("AudioPlayWorker quit")
        self.quit_signal.emit(True)   

