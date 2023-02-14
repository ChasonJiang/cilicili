from queue import Full, Queue
import sys
from time import sleep, time
import cv2
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import ffmpeg
import numpy as np

from .AudioContext import AudioContext
import logging
# logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO) # DEBUG
LOGGER=logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class AudioDecodeWorker(QObject):
    buffer_queue_full_signal = pyqtSignal(str)
    decoder_init_status_signal = pyqtSignal(int)
    req_clear_buffer_queue_signal = pyqtSignal()
    decode_end_signal = pyqtSignal()
    abuffer_exception_signal = pyqtSignal(int)

    def __init__(self, audio_context,  buffer_queue, ss:int=0, base_pts=0, thread_queue_size=8):
        super(AudioDecodeWorker, self).__init__()
        # LOGGER.info("init AudioDecodeWorker")
        assert isinstance(audio_context, AudioContext)
        assert isinstance(buffer_queue,Queue)   
        self._isQuit = False
        self.buffer_queue = buffer_queue
        self.thread_queue_size = thread_queue_size
        self.decoder = None
        self.audio_context=audio_context
        self.ss = ss # ms, int
        self.base_pts = base_pts
        self.frame_rate = self.audio_context.frame_rate
        self.sample_rate = 192000
        self.frame_size = round(2*self.sample_rate*16*(1.0/self.frame_rate)/8)
        self.name = "AudioDecodeWorker"
        self.process = None

    def quit(self):
        self._isQuit = True

    def destroy(self):
        del self.decoder 
        self.decoder = None
        self.req_clear_buffer_queue_signal.emit()


    def work(self):
        # LOGGER.info("thread id of AudioDecodeWorker is {}".format(QThread.currentThreadId()))   
        try:
            self.decoder = self.init_decoder(self.audio_context,self.ss)
        except :
            self.decoder_init_status_signal.emit(0)

        self.decoder_init_status_signal.emit(1)
        self.write_buffer(self.audio_context)

    def write_buffer(self, audio_context:AudioContext):
        curr_frame_pts = 0
        curr_frame_index = 0
        zero_byte_counter = 0
        try:
            while True:
                if  self._isQuit:
                    # LOGGER.info("AudioDecodeWorker quit")
                    break 

                if self.buffer_queue.full():
                    # LOGGER.debug("audio frame buffer queue is full")
                    self.buffer_queue_full_signal.emit("audio_decode_worker")
                # 计算音频每帧的字节数 channel * sample_rate * seconds_per_frame / 8 

                frame_bytes=self.decoder.stdout.read(self.frame_size)
                if len(frame_bytes)==0:
                    self.decode_end_signal.emit()
                    LOGGER.debug("audio frame over")
                    break
                    # if zero_byte_counter>5:
                    #     self.decode_end_signal.emit()
                    #     LOGGER.debug("audio frame over")
                    #     break
                    # zero_byte_counter+=1
                    # sleep(2)
                    # continue
        
                zero_byte_counter = 0

                frame = (
                    np
                    .frombuffer(frame_bytes, np.int16)
                    .tobytes()
                )
                # print("read audio frame")
                curr_frame_pts = 1000.0/self.frame_rate * curr_frame_index + self.ss + self.base_pts
                curr_frame_index += 1
                # sleep(0.1)
                self.buffer_queue.put({"data":frame,"pts":curr_frame_pts})

                # LOGGER.info("read audio frame")
            # pass
        except:
            self.abuffer_exception_signal.emit(curr_frame_pts)
            LOGGER.warning("audio frame buffer exception")
            RuntimeError("audio frame buffer exception")
        finally:
            self.decoder.stdout.close()
            self.decoder.wait()
            LOGGER.info("AudioDecodeWorker quited")
            
        LOGGER.debug("total audio frames {}".format(curr_frame_index+1))
        
    def init_decoder(self,audio_context:AudioContext, ss:int=0):
        decoder = None
        try:
            if audio_context.source == 'file':
                    decoder=(
                            ffmpeg
                            .input(
                                    audio_context.url,
                                    ss=(audio_context.start_time+ss)/1000.0,
                                    loglevel="error",
                                    thread_queue_size=self.thread_queue_size,
                                    )
                            .output("-" , 
                                    map="0:a",
                                    format='s16le', 
                                    ac="2", 
                                    ar=str(self.sample_rate),
                                    # af="asyncts=compensate=1"
                                    )
                            .run_async(pipe_stdout=True,pipe_stderr=True)
                        )

            elif audio_context.source == "network":
                for k in audio_context.req_header.keys():
                    audio_context.req_header[k.lower()] = audio_context.req_header[k]
                
                # if "user-agent"  not in audio_context.req_header.keys():
                #     audio_context.req_header["user-agent" ]=None
                # if "referer"  not in audio_context.req_header.keys():
                #     audio_context.req_header["user-referer" ]=None                
                if "user-agent" and "referer" in audio_context.req_header.keys():
                    decoder=(
                        ffmpeg
                        .input(
                                audio_context.url, 
                                user_agent=audio_context.req_header["user-agent"], 
                                referer=audio_context.req_header["referer"], 
                                headers=audio_context.req_header, 
                                method=audio_context.req_method, 
                                ss=(audio_context.start_time+ss)/1000.0,
                                loglevel="error",
                                thread_queue_size=self.thread_queue_size
                                )
                            .output("-" , 
                                    map="0:a",
                                    format='s16le', 
                                    ac="2", 
                                    ar=str(self.sample_rate),
                                    # af="asyncts=compensate=1"
                                    )
                            .run_async(cmd=["ffmpeg","-rw_timeout","5000000"],pipe_stdout=True,pipe_stderr=True)
                        )
                elif "user-agent"  in audio_context.req_header.keys():
                    decoder=(
                        ffmpeg
                        .input(
                                audio_context.url, 
                                user_agent=audio_context.req_header["user-agent"], 
                                headers=audio_context.req_header, 
                                method=audio_context.req_method, 
                                ss=(audio_context.start_time+ss)/1000.0,
                                loglevel="error",
                                thread_queue_size=self.thread_queue_size
                                )
                            .output("-" , 
                                    map="0:a",
                                    format='s16le', 
                                    ac="2", 
                                    ar=str(self.sample_rate),
                                    # af="asyncts=compensate=1"
                                    )
                            .run_async(pipe_stdout=True,pipe_stderr=True)
                    )
                elif "referer" in audio_context.req_header.keys():
                    decoder=(
                            ffmpeg
                            .input(
                                audio_context.url, 
                                referer=audio_context.req_header["referer"], 
                                headers=audio_context.req_header, 
                                method=audio_context.req_method, 
                                ss=(audio_context.start_time+ss)/1000.0,
                                loglevel="error",
                                thread_queue_size=self.thread_queue_size
                                    )
                            .output("-" , 
                                    map="0:a",
                                    format='s16le', 
                                    ac="2", 
                                    ar=str(self.sample_rate),
                                    # af="asyncts=compensate=1"
                                    )
                            .run_async(pipe_stdout=True,pipe_stderr=True)
                        )
                else:
                    decoder=(
                            ffmpeg
                            .input(
                                audio_context.url, 
                                headers=audio_context.req_header, 
                                method=audio_context.req_method, 
                                ss=(audio_context.start_time+ss)/1000.0,
                                loglevel="error",
                                thread_queue_size=self.thread_queue_size
                                    )
                            .output("-" , 
                                    map="0:a",
                                    format='s16le', 
                                    ac="2", 
                                    ar=str(self.sample_rate),
                                    # af="asyncts=compensate=1"
                                    )
                            .run_async(pipe_stdout=True,pipe_stderr=True)
                        )
        except:
            LOGGER.error("audio decoder 获取失败！")
            raise RuntimeError("audio decoder 获取失败！")

        return decoder









