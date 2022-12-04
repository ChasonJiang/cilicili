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
from SuperResolution.HandlerCmd import HandlerCmd
from SuperResolution.SRStatusCode import SRStatusCode as SRSC
from SuperResolution.SRContext import SRContext
from .PipeLinker import PipeLinker

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

    def __init__(self, video_context, buffer_queue, ss:int=0, base_pts=0, sr_mode=None,sr_context=None,thread_queue_size=8):
        super(VideoDecodeWorker, self).__init__()
        # LOGGER.info("init VideoDecodeWorker")
        assert isinstance(video_context, VideoContext)
        assert isinstance(buffer_queue,Queue)   
        self._isQuit = False
        self.buffer_queue = buffer_queue
        self.thread_queue_size = thread_queue_size
        self.sr_mode = sr_mode
        self.sr_context = sr_context
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
        if self.sr_mode is not None:
            self.write_buffer_sr_mode(self.video_context,self.sr_context)
        else:
            self.write_buffer(self.video_context)

    def write_buffer(self, video_context:VideoContext):
        curr_frame_pts = 0
        curr_frame_index = 0
        frame_size = video_context.frame_width \
            * video_context.frame_height \
            * video_context.frame_channels
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
                frame_bytes=self.decoder.stdout.read(frame_size)
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
        LOGGER.debug("write_buffer_sr_mode")
        sr_context.cmdPipe.send(HandlerCmd(HandlerCmd.Switch,self.sr_mode))
        self.pipeLinker = PipeLinker(self.decoder,
                            sr_context.outputDataPipe,
                            [video_context.frame_height, 
                            video_context.frame_width, 
                            video_context.frame_channels])
        self.pipeLinkerThread =QThread()
        self.pipeLinker.moveToThread(self.pipeLinkerThread)
        self.pipeLinkerThread.started.connect(self.pipeLinker.work)
        # self.pipeLinkerThread.finished.connect(self.pipeLinker.quit)
        self.pipeLinkerThread.start()


        try:
            
            if sr_context.msgPipe.recv() != SRSC.InferencerStarted:
                LOGGER.error("Inferencer Load failed")
                raise RuntimeError("Inferencer Load failed")

            while True:
                if self._isQuit:
                    LOGGER.info("VideoDecodeWorker quit")

                    # self.decoder.terminate()
                    # sr_context.cmdPipe.send(HandlerCmd(HandlerCmd.Quit))
                    break 
                if sr_context.msgPipe.poll():
                    self.checkSrMsg(sr_context.msgPipe.recv())
                if self.buffer_queue.full():
                    # LOGGER.debug("video frame buffer queue is full")
                    self.buffer_queue_full_signal.emit("video_decode_worker")
                
                frame=sr_context.inputDataPipe.recv()
                # print(frame)
                LOGGER.debug("read video frame")
                if frame is None:
                    self.decode_end_signal.emit()
                    LOGGER.info("video frame over")
                    break

                curr_frame_pts = 1000.0/video_context.frame_rate * curr_frame_index + self.ss + self.base_pts
                curr_frame_index += 1
                self.buffer_queue.put({"data":frame,"pts":curr_frame_pts})

        except Exception as e:
            print(e)
            self.vbuffer_exception_signal.emit(curr_frame_pts)
            LOGGER.error("video frame buffer exception")
            # RuntimeError("video frame buffer exception")
        finally:
            self.pipeLinker.quit()
            self.pipeLinkerThread.quit()
            self.pipeLinkerThread.wait(1000)    
            self.decoder.stdout.close()
            self.decoder.wait()
        # RuntimeError("video frame buffer exception")
        LOGGER.debug("total video frames {}".format(curr_frame_index+1))


    def checkSrMsg(self,statusCode:int):
        if statusCode == SRSC.InferencerStarted:
            LOGGER.debug("SRSC.InferencerStarted")
        elif statusCode == SRSC.IoError:
            LOGGER.debug("SRSC.IoError")
        elif statusCode == SRSC.LoadInferencerError:
            LOGGER.debug("SRSC.LoadInferencerError")
        
        
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









