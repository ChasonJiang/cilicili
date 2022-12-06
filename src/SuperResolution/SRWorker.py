import json
import logging
from multiprocessing.connection import PipeConnection
import os
from time import sleep
from PyQt5.QtCore import *
import ffmpeg
import numpy as np
from SuperResolution.ClassLoader import classloader

from player.utils.VideoContext import VideoContext

from .SRContext import SRContext

from .Inferencer import Inferencer
from .SRStatusCode import SRStatusCode as SRSC
LOGGER=logging.getLogger()

class SRWorker(QObject):
    def __init__(self,decoderContext,sr_context):
        super(SRWorker, self).__init__()
        self._isQuit = False
        # self.buffer_queue = buffer_queue
        self.thread_queue_size:int = decoderContext["thread_queue_size"]
        self.sr_mode:str = decoderContext["sr_mode"]
        self.sr_context:SRContext = sr_context
        self.decoder = None
        self.video_context:VideoContext=decoderContext["video_context"]
        self.ss:int = decoderContext["ss"] # ms, int
        self.base_pts:int = decoderContext["base_pts"] # ms, int
        self.inferencer=None
        self.inferencerInfo:dict = None

    def loadInferencerInfo(self):
        try:
            with open(os.path.join(os.path.dirname(__file__),"SuperResolutionInferencer","SuperResolutionInferencerRegister.json"),"r") as f:
                self.inferencerInfo = json.loads(f.read())
        except IOError:
            print("Error reading SuperResolutionInferencerRegister.json")
            LOGGER.error("Error reading SuperResolutionInferencerRegister.json")
            self.sr_context.msgPipe.send(SRSC.LoadInferencerInfoFailed)
            raise RuntimeError("Load InferencerInfo Failed")
            # LOGGER.error(os.path.join(os.path.dirname(__file__),"SuperResolutionInferencer","SuperResolutionInferencerRegister.json"))
            


    def loadInferencer(self,className:str, classPath:str):
        try:
            inferencer:Inferencer =classloader("SuperResolution.SuperResolutionInferencer."+classPath,className)
        except:
            print("LoadInferencer Error")
            LOGGER.error("LoadInferencer Error")
            self.sr_context.msgPipe.send(SRSC.LoadInferencerFailed)
            raise RuntimeError("Load Inferencer Failed")
        return inferencer()

    def quit(self):
        self._isQuit = True


    def work(self):
        # print("thread id of VideoDecodeWorker is {}".format(QThread.currentThreadId()))   
        # print("VideoDecodeWorker run work")
        try:
            self.decoder = self.init_decoder(self.video_context,self.ss)
        except :
            self.sr_context.msgPipe.send(SRSC.DecoderInitFailed)
            return

        if self.sr_mode is not None:
            try:
                self.loadInferencerInfo()
                class_name=self.inferencerInfo["Inferencer"][self.sr_mode]["ClassName"]
                class_path=self.inferencerInfo["Inferencer"][self.sr_mode]["ClassPath"]
                self.inferencer:Inferencer = self.loadInferencer(class_name,class_path)
            except:
                return

        self.sr_context.msgPipe.send(SRSC.DecoderInitSuccess)
        self.process(self.video_context)


    def process(self, video_context:VideoContext):
        frame_size = video_context.frame_width \
            * video_context.frame_height \
            * video_context.frame_channels
        self.sr_context.msgPipe.send(SRSC.Started)
        try:
            while True:
                if self._isQuit:
                    print("SRWorker quit")
                    LOGGER.info("SRWorker quit")
                    # self.decoder.terminate()
                    break 

                # print("read video frame")
                frame_bytes=self.decoder.stdout.read(frame_size)
                if not frame_bytes:
                    self.sr_context.outputDataPipe.send(None)
                    LOGGER.info("video frame over")
                    break

                frame = (
                    np
                    .frombuffer(frame_bytes, np.uint8)
                    .reshape([video_context.frame_height, 
                            video_context.frame_width, 
                            video_context.frame_channels])
                )

                if self.sr_mode is not None:
                    frame = self.inferencer.process(frame)

                if frame is not None:
                    self.sr_context.outputDataPipe.send(frame)

        except:
            self.sr_context.msgPipe.send(SRSC.ProcessException)
            print("video frame buffer exception")
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









