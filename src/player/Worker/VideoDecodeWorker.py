from multiprocessing import Pipe
from queue import Full, Queue
import sys
from time import sleep, time
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import ffmpeg
import numpy as np
from VideoProcessor.HandlerCmd import HandlerCmd
from VideoProcessor.SRStatusCode import SRStatusCode as SRSC
from VideoProcessor.SRContext import SRContext
from ..Context.VideoContext import VideoContext
import logging
# logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO) # DEBUG
# LOGGER=logging.getLogger("VideoDecodeWorkerLogger")
LOGGER=logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class VideoDecodeWorker(QObject):
    buffer_queue_full_signal = pyqtSignal(str)
    buffer_queue_empty_signal = pyqtSignal()
    decoder_init_status_signal = pyqtSignal(int)
    req_clear_buffer_queue_signal = pyqtSignal()
    decode_end_signal = pyqtSignal()
    vbuffer_exception_signal = pyqtSignal(int)

    def __init__(self, video_context, buffer_queue, ss:int=0, base_pts=0, sr_mode:bool=False,sr_context=None,thread_queue_size=8):
        super(VideoDecodeWorker, self).__init__()
        # LOGGER.info("init VideoDecodeWorker")
        assert isinstance(video_context, VideoContext)
        assert isinstance(buffer_queue,Queue)   
        self._isQuit = False
        self.buffer_queue = buffer_queue
        self.thread_queue_size = thread_queue_size
        self.sr_mode = sr_mode
        self.sr_context:SRContext = sr_context
        self.video_context=video_context
        self.ss = ss # ms, int
        self.base_pts = base_pts # ms, int
        self.before_empty=False
        self.buffer_queue_empty_signal.connect(self.change_before_empty)


    def quit(self):
        self._isQuit = True

    def work(self):
        curr_frame_pts = 0
        curr_frame_index = 0
        decoderContext = {
            "video_context": self.video_context,
            "ss":self.ss,
            "base_pts":self.base_pts,
            "thread_queue_size":self.thread_queue_size,
            "sr_mode":self.sr_mode,
        }
        self.sr_context.cmdPipe.send(HandlerCmd(HandlerCmd.Start,decoderContext))

        try:
            
            self.checkSrMsg(self.sr_context.msgPipe.recv())

            while True:
                if self._isQuit:
                    # LOGGER.info("VideoDecodeWorker quit")
                    self.sr_context.cmdPipe.send(HandlerCmd(HandlerCmd.QuitSRWorker))
                    self.sr_context.msgPipe.recv()
                    self.clear_pipe()
                    self.sr_context.cmdPipe.send(HandlerCmd(HandlerCmd.QuitSRThread))
                    # self.decoder.terminate()
                    # sr_context.cmdPipe.send(HandlerCmd(HandlerCmd.Quit))
                    break 
                if self.sr_context.msgPipe.poll():
                    self.checkSrMsg(self.sr_context.msgPipe.recv())
                if self.buffer_queue.full() and self.before_empty:
                    LOGGER.debug("video frame buffer queue is full")
                    self.buffer_queue_full_signal.emit("video_decode_worker")
                    self.before_empty=False
                # if not self.sr_context.inputDataPipe.poll() and self.buffer_queue.empty():
                #     self.before_empty=True
                
                frame=self.sr_context.inputDataPipe.recv()
                # print("frame")
                # LOGGER.debug("read video frame")
                if frame is None:
                    self.decode_end_signal.emit()
                    LOGGER.info("video frame over")
                    break

                curr_frame_pts = 1000.0/self.video_context.frame_rate * curr_frame_index + self.ss + self.base_pts
                curr_frame_index += 1
                self.buffer_queue.put({"data":frame,"pts":curr_frame_pts})

        except Exception as e:
            print(e)
            self.vbuffer_exception_signal.emit(curr_frame_pts)
            LOGGER.error(e)
        finally:
            LOGGER.info("VideoDecodeWorker quited")

        LOGGER.debug("total video frames {}".format(curr_frame_index+1))


    def change_before_empty(self,):
        print("change_before_empty")
        self.before_empty=True


    def checkSrMsg(self,statusCode:int):
        if statusCode == SRSC.Started:
            return True
        elif statusCode == SRSC.IoError:
            raise RuntimeError("SRSC.IoError")
        elif statusCode == SRSC.LoadInferencerFailed:
            raise RuntimeError("SRSC.LoadInferencer ")
        elif statusCode == SRSC.LoadInferencerInfoFailed:
            raise RuntimeError("SRSC.LoadInferencerInfoFailed")
        
    def clear_pipe(self):
        LOGGER.debug("clear pipe...")
        while self.sr_context.inputDataPipe.poll():
            self.sr_context.inputDataPipe.recv()
