from queue import Full, Queue
import sys
from time import sleep, time
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import ffmpeg
import numpy as np

from SuperResolution.SRContext import SRContext

from .VideoContext import VideoContext
import logging
# logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO) # DEBUG
# LOGGER=logging.getLogger("VideoDecodeWorkerLogger")
LOGGER=logging.getLogger()

class VideoDecodeWorker(QObject):
    buffer_queue_full_signal = pyqtSignal(str)
    decoder_init_status_signal = pyqtSignal(int)
    req_clear_buffer_queue_signal = pyqtSignal()
    decode_end_signal = pyqtSignal()
    vbuffer_exception_signal = pyqtSignal(int)

    def __init__(self, video_context, buffer_queue, ss:int=0, base_pts=0, thread_queue_size=8):
        super(VideoDecodeWorker, self).__init__()
        # LOGGER.info("init VideoDecodeWorker")
        assert isinstance(video_context, VideoContext)
        assert isinstance(buffer_queue,Queue)   
        self._isQuit = False
        self.buffer_queue = buffer_queue
        self.thread_queue_size = thread_queue_size
        self.decoder = None
        self.video_context=video_context
        self.ss = ss # ms, int
        self.base_pts = base_pts # ms, int
        self.name = "VideoDecodeWorker"
        self.process=None

    def quit(self):
        self._isQuit = True

    def destroy(self):
        del self.decoder 
        self.decoder = None
        self.req_clear_buffer_queue_signal.emit()

    def work(self):
        # print("thread id of VideoDecodeWorker is {}".format(QThread.currentThreadId()))   
        # print("VideoDecodeWorker run work")
        try:
            self.decoder = self.init_decoder(self.video_context,self.ss)
        except :
            self.decoder_init_status_signal.emit(0)

        self.decoder_init_status_signal.emit(1)
        self.write_buffer(self.video_context)

    def write_buffer(self, video_context:VideoContext):
        curr_frame_pts = 0
        curr_frame_index = 0
        try:
            while True:
                if self._isQuit:
                    LOGGER.info("VideoDecodeWorker quit")
                    # self.decoder.terminate()
                    break 

                if self.buffer_queue.full():
                    # LOGGER.debug("video frame buffer queue is full")
                    self.buffer_queue_full_signal.emit("video_decode_worker")
                # LOGGER.debug("read video frame")
                frame_bytes=self.decoder.stdout.read(video_context.frame_width \
                                        * video_context.frame_height \
                                        * video_context.frame_channels)
                if not frame_bytes:
                    self.decode_end_signal.emit()
                    LOGGER.info("video frame over")
                    break


                frame = (
                    np
                    .frombuffer(frame_bytes, np.uint8)
                    .reshape([video_context.frame_height, 
                            video_context.frame_width, 
                            video_context.frame_channels])
                )
                
                curr_frame_pts = 1000.0/video_context.frame_rate * curr_frame_index + self.ss + self.base_pts
                curr_frame_index += 1
                self.buffer_queue.put({"data":frame,"pts":curr_frame_pts})

        except:
            self.vbuffer_exception_signal.emit(curr_frame_pts)
            LOGGER.error("video frame buffer exception")
            RuntimeError("video frame buffer exception")
        finally:
            self.decoder.stdout.close()
            self.decoder.wait()
            
            # RuntimeError("video frame buffer exception")
        LOGGER.debug("total video frames {}".format(curr_frame_index+1))
    

    def write_buffer_sr_mode(self, video_context:VideoContext,sr_context:SRContext):
        curr_frame_pts = 0
        curr_frame_index = 0

        try:
            while True:
                if self._isQuit:
                    LOGGER.info("VideoDecodeWorker quit")
                    # self.decoder.terminate()
                    break 

                if self.buffer_queue.full():
                    # LOGGER.debug("video frame buffer queue is full")
                    self.buffer_queue_full_signal.emit("video_decode_worker")
                # LOGGER.debug("read video frame")
                frame_bytes=self.decoder.stdout.read(video_context.frame_width \
                                        * video_context.frame_height \
                                        * video_context.frame_channels)
                if not frame_bytes:
                    self.decode_end_signal.emit()
                    LOGGER.info("video frame over")
                    break


                frame = (
                    np
                    .frombuffer(frame_bytes, np.uint8)
                    .reshape([video_context.frame_height, 
                            video_context.frame_width, 
                            video_context.frame_channels])
                )
                
                curr_frame_pts = 1000.0/video_context.frame_rate * curr_frame_index + self.ss + self.base_pts
                curr_frame_index += 1
                self.buffer_queue.put({"data":frame,"pts":curr_frame_pts})

        except:
            self.vbuffer_exception_signal.emit(curr_frame_pts)
            LOGGER.error("video frame buffer exception")
            RuntimeError("video frame buffer exception")
        finally:
            self.decoder.stdout.close()
            self.decoder.wait()
            
            # RuntimeError("video frame buffer exception")
        LOGGER.debug("total video frames {}".format(curr_frame_index+1))

        
    def init_decoder(self,video_context:VideoContext, ss:int=0):
        # print("video init_decoder")
        decoder = None
        try:
            if video_context.source == 'file':
                    decoder=(
                            ffmpeg
                            .input(
                                    video_context.url,
                                    ss=(video_context.start_time+ss)/1000.0,
                                    loglevel="error",
                                    thread_queue_size=self.thread_queue_size,
                                    )
                            .output("-" , 
                                    map="0:v",
                                    vsync="cfr",
                                    r=video_context.frame_rate,
                                    shortest =None,
                                    format='rawvideo', 
                                    pix_fmt='rgb24'
                                    )
                            .run_async(pipe_stdout=True,pipe_stderr=True)
                        )

            elif video_context.source == "network":
                for k in video_context.req_header.keys():
                    video_context.req_header[k.lower()] = video_context.req_header[k]
                
                # if "user-agent"  not in video_context.req_header.keys():
                #     video_context.req_header["user-agent" ]=None
                # if "referer"  not in video_context.req_header.keys():
                #     video_context.req_header["user-referer" ]=None                
                if "user-agent" and "referer" in video_context.req_header.keys():
                    decoder=(
                        ffmpeg
                        .input(
                                video_context.url, 
                                user_agent=video_context.req_header["user-agent"], 
                                referer=video_context.req_header["referer"], 
                                headers=video_context.req_header, 
                                method=video_context.req_method, 
                                ss=(video_context.start_time+ss)/1000.0,
                                loglevel="error",
                                )
                        .output("-" , 
                                format='rawvideo', 
                                pix_fmt='rgb24',
                                thread_queue_size=self.thread_queue_size,
                                )
                        .run_async(pipe_stdout=True,pipe_stderr=True)
                    )
                elif "user-agent"  in video_context.req_header.keys():
                       decoder=(
                        ffmpeg
                        .input(
                                video_context.url, 
                                user_agent=video_context.req_header["user-agent"], 
                                headers=video_context.req_header, 
                                method=video_context.req_method, 
                                ss=(video_context.start_time+ss)/1000.0,
                                loglevel="error",
                                )
                        .output("-" , 
                                format='rawvideo', 
                                pix_fmt='rgb24',
                                thread_queue_size=self.thread_queue_size,
                                )
                        .run_async(pipe_stdout=True,pipe_stderr=True)
                    )
                elif "referer" in video_context.req_header.keys():
                    decoder=(
                        ffmpeg
                        .input(
                                video_context.url, 
                                referer=video_context.req_header["referer"], 
                                headers=video_context.req_header, 
                                method=video_context.req_method, 
                                ss=(video_context.start_time+ss)/1000.0,
                                loglevel="error",
                                )
                        .output("-" , 
                                format='rawvideo', 
                                pix_fmt='rgb24',
                                thread_queue_size=self.thread_queue_size,
                                )
                        .run_async(pipe_stdout=True,pipe_stderr=True)
                    )
                else:
                    decoder=(
                        ffmpeg
                        .input(
                                video_context.url, 
                                user_agent=video_context.req_header["user-agent"], 
                                referer=video_context.req_header["referer"], 
                                headers=video_context.req_header, 
                                method=video_context.req_method, 
                                ss=(video_context.start_time+ss)/1000.0,
                                loglevel="error",
                                )
                        .output("-" , 
                                format='rawvideo', 
                                pix_fmt='rgb24',
                                thread_queue_size=self.thread_queue_size,
                                )
                        .run_async(pipe_stdout=True,pipe_stderr=True)
                    )
        except:
            LOGGER.error("video decoder 获取失败！")
            raise RuntimeError("video decoder 获取失败！")

        return decoder









