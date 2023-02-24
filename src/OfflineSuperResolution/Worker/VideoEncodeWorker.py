from multiprocessing import Pipe
from queue import Full, Queue
import sys
from time import perf_counter, sleep, time
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import ffmpeg
import numpy as np
import torch
from VideoProcessor.HandlerCmd import HandlerCmd
from VideoProcessor.SRStatusCode import SRStatusCode as SRSC
from VideoProcessor.SRContext import SRContext
from Player.Context.VideoContext import VideoContext
import logging
# logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO) # DEBUG
# LOGGER=logging.getLogger("VideoDecodeWorkerLogger")
LOGGER=logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class VideoEncodeWorker(QObject):
    encoder_init_status_signal = pyqtSignal(int)
    encode_end_signal = pyqtSignal()
    update_progress_signal = pyqtSignal(int)
    send_log_signal = pyqtSignal(str)
    process_end_signal = pyqtSignal()

    def __init__(self, video_context, save_path:str, sr_mode:bool=False,sr_context=None,multiplier:int=1,thread_queue_size=8):
        super(VideoEncodeWorker, self).__init__()
        # LOGGER.info("init VideoDecodeWorker")
        assert isinstance(video_context, VideoContext)
        assert save_path is not None
        assert multiplier != 0
        self.save_path = save_path
        self._isQuit = False
        self.thread_queue_size = thread_queue_size
        self.sr_mode = sr_mode
        self.sr_context:SRContext = sr_context
        self.multiplier = multiplier
        self.video_context=video_context
        self.frame_width = multiplier*self.video_context.frame_width
        self.frame_height = multiplier*self.video_context.frame_height
        self.encoder = None


    def initEncoder(self):
        self.encoder = (
            ffmpeg
            .input('pipe:', 
                   format='rawvideo', 
                   framerate=self.video_context.frame_rate, 
                   pix_fmt='rgb24',
                   loglevel="error", 
                   s='{}x{}'.format(self.frame_width, self.frame_height)
                   )
            # .input('pipe:', format='rawvideo', framerate=self.video_context.frame_rate, pix_fmt='rgb24')

            .output(self.save_path, qp="0", preset="ultrafast")
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )
        self.send_log_signal.emit("Encoder is ready")


    def quit(self):
        self._isQuit = True

    def work(self):
        self.initEncoder()
        curr_frame_pts = 0
        curr_frame_index = 0
        decoderContext = {
            "video_context": self.video_context,
            "ss":0,
            "base_pts":0,
            "thread_queue_size":self.thread_queue_size,
            "sr_mode":self.sr_mode,
        }
       
        self.sr_context.cmdPipe.send(HandlerCmd(HandlerCmd.Start,decoderContext))
        self.send_log_signal.emit("Requesting Super Resolution")

        try:
            self.checkSrMsg(self.sr_context.msgPipe.recv())
            self.send_log_signal.emit("Super Resolution started")
            while True:
                if self._isQuit:

                    break 

                if self.sr_context.msgPipe.poll():
                    self.checkSrMsg(self.sr_context.msgPipe.recv())
                # print("receiving frame")
                start_time = perf_counter()
                frame:torch.Tensor=self.sr_context.inputDataPipe.recv()
                if frame is None:
                    self.encoder.stdin.close()
                    # self.encode_end_signal.emit()
                    # LOGGER.info("video frame over")
                    break
                frame:np.ndarray = frame[:,:,:3].cpu().numpy()

                self.encoder.stdin.write(frame.astype(np.uint8).tobytes())
                curr_frame_pts = 1000.0/self.video_context.frame_rate * curr_frame_index
                progress = 100.0*curr_frame_pts/self.video_context.duration
                self.update_progress_signal.emit(round(progress))
                self.send_log_signal.emit(f"Frame: {curr_frame_index} | {perf_counter()-start_time:.3f} second per frame")

                curr_frame_index += 1

        except Exception as e:
            LOGGER.error(e)
        finally:
            self.sr_context.cmdPipe.send(HandlerCmd(HandlerCmd.QuitSRWorker))
            self.clear_pipe()
            self.sr_context.cmdPipe.send(HandlerCmd(HandlerCmd.QuitSRThread))
            if self.encoder is not None:
                self.send_log_signal.emit("Super-Resolution is done!")
                self.send_log_signal.emit("Wait for encoding to complete...")
                # self.encoder.wait()
                self.send_log_signal.emit("Encoding completed")
            self.process_end_signal.emit()
            LOGGER.info("VideoEncodeWorker quited")

        LOGGER.debug("total video frames {}".format(curr_frame_index+1))


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
