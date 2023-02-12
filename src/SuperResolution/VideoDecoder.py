import json
import logging
from multiprocessing.connection import PipeConnection
import os
# from queue import Queue
from multiprocessing import Queue
# from torch.multiprocessing import Queue
from time import sleep
from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *
from threading import Thread
import ffmpeg
import numpy as np
import torch
from SuperResolution.ClassLoader import classLoader

from player.utils.VideoContext import VideoContext

from .SRContext import SRContext

from .Inferencer import Inferencer
from .SRStatusCode import SRStatusCode as SRSC
LOGGER=logging.getLogger()

class VideoDecoder(Thread):
    def __init__(self,decoderContext:dict, sr_context:SRContext, frame_buffer_queue:Queue=None):
        super(VideoDecoder, self).__init__()
        self.frame_buffer_queue = frame_buffer_queue
        self._isQuit = False
        # self.buffer_queue = buffer_queue
        self.thread_queue_size:int = decoderContext["thread_queue_size"]
        self.sr_context:SRContext = sr_context
        self.decoder = None
        self.video_context:VideoContext=decoderContext["video_context"]
        self.ss:int = decoderContext["ss"] # ms, int
        self.base_pts:int = decoderContext["base_pts"] # ms, int
        self.sr_mode:bool = decoderContext["sr_mode"]

        self.device = torch.device("cuda:0")

    def quit(self):
        self._isQuit = True

    # def work(self):
    def run(self):
        # print("thread id of VideoDecodeWorker is {}".format(QThread.currentThreadId()))   
        # print("VideoDecodeWorker run work")
        
        try:
            self.decoder = self.init_decoder(self.video_context,self.ss)
        except :
            self.sr_context.msgPipe.send(SRSC.DecoderInitFailed)
            return

        self.sr_context.msgPipe.send(SRSC.DecoderInitSuccess)
        self.process(self.video_context)
        
    def send(self, frame:np.ndarray):
        if self.sr_mode:
            self.frame_buffer_queue.put(frame)
        else:
            self.sr_context.outputDataPipe.send(frame)

    def process(self, video_context:VideoContext):
        
        frame_size = video_context.frame_width \
            * video_context.frame_height \
            * video_context.frame_channels
        self.sr_context.msgPipe.send(SRSC.Started)

        zero_byte_counter = 0
        try:
            while True:
                if self._isQuit:
                    print("VideoDecoder quit")
                    LOGGER.info("VideoDecoder quit")
                    # self.decoder.terminate()
                    break 

                # print("read video frame")
                frame_bytes=self.decoder.stdout.read(frame_size)
                if len(frame_bytes)==0:
                    
                    if zero_byte_counter>5:
                        self.send(None)
                        print("video decode over")
                        LOGGER.info("video frame over")
                        break
                    zero_byte_counter+=1
                    sleep(2)
                    continue
        
                zero_byte_counter = 0
                
                frame = (
                    np
                    .frombuffer(frame_bytes, np.uint8)
                    .reshape([video_context.frame_height, 
                            video_context.frame_width, 
                            video_context.frame_channels])
                )

                self.send(frame)

        except Exception as e:
            self.sr_context.msgPipe.send(SRSC.ProcessException)
            print("video frame buffer exception:\n",e)
            RuntimeError("video frame buffer exception")
        finally:
            self.decoder.stdout.close()
            self.decoder.wait()

    def init_decoder(self,video_context:VideoContext, ss:int=0):
        # print("video init_decoder")
        decoder = None
        try:
            if video_context.source == 'file':
                    decoder=(
                            ffmpeg
                            .input(
                                    video_context.url,
                                    rw_timeout=1.5*1000000,
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
                                    map="0:v",
                                    vsync="cfr",
                                    r=video_context.frame_rate,
                                    shortest =None,
                                    format='rawvideo', 
                                    pix_fmt='rgb24'
                                    )
                            .run_async(cmd=["ffmpeg","-rw_timeout","5000000"],pipe_stdout=True,pipe_stderr=True)
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
                                    map="0:v",
                                    vsync="cfr",
                                    r=video_context.frame_rate,
                                    shortest =None,
                                    format='rawvideo', 
                                    pix_fmt='rgb24'
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
                                    map="0:v",
                                    vsync="cfr",
                                    r=video_context.frame_rate,
                                    shortest =None,
                                    format='rawvideo', 
                                    pix_fmt='rgb24'
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
                                    map="0:v",
                                    vsync="cfr",
                                    r=video_context.frame_rate,
                                    shortest =None,
                                    format='rawvideo', 
                                    pix_fmt='rgb24'
                                    )
                            .run_async(pipe_stdout=True,pipe_stderr=True)
                    )
        except:
            LOGGER.error("video decoder 获取失败！")
            raise RuntimeError("video decoder 获取失败！")

        return decoder


