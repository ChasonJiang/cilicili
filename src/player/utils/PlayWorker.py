import logging
from queue import Queue
from time import sleep
from PyQt5.QtCore import *
from SuperResolution.SRContext import SRContext
from Tools.BinaryNeuron import BinaryNeuron
from player.utils.DisplayDevice import DisplayDevice
from player.utils.RTSRWorker import RTSRWorker

# import pycuda.driver
# # import pycuda.gl.autoinit
# from player.utils.CudaAutoInit import *
# import pycuda.gl

# from player.utils.AVPlayWorker import AVPlayWorker
from .PlayStatusController import PlayStatusController
from .PlayClock import PlayClock

from .VideoDecodeWorker import VideoDecodeWorker
from .MediaInfo import MediaInfo
from .VideoContext import VideoContext
from .AudioContext import AudioContext
from .AudioDecodeWorker import AudioDecodeWorker
from .AudioPlayWorker import AudioPlayWorker
from .VideoPlayWorker  import VideoPlayWorker
# logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO) # DEBUG
LOGGER=logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
class PlayWorker(QObject):
    play_signal = pyqtSignal(MediaInfo)
    play_pause_signal = pyqtSignal()
    play_resume_signal = pyqtSignal()
    play_end_signal = pyqtSignal()
    play_seek_signal = pyqtSignal(int)
    update_playback_progress = pyqtSignal(int)
    get_AVContext_failed = pyqtSignal(str)
    wait_buffer_signal = pyqtSignal()
    buffer_ok_signal = pyqtSignal()
    media_info_exception_signal = pyqtSignal(str)
    send_duration_time = pyqtSignal(int)
    shutdown_signal = pyqtSignal(bool)

    
    def __init__(self, videoDevice:DisplayDevice, audioDevice, srContext=None,vQueueSize=10,aQueueSize=10):
        super(PlayWorker, self).__init__()
        LOGGER.info("init PlayWorker")
        self.videoDevice = videoDevice
        self.audioDevice = audioDevice
        self.vQueueSize = vQueueSize
        self.aQueueSize = aQueueSize
        self.isFirstLoad = True
        self.shutdown_signal.connect(self.shutdown)
        self.enable_rtsr = False
        self.srContext = srContext
        self.inited = False
        self.play_signal.connect(self.play)



    def init(self,mediaInfo:MediaInfo):
        self.mediaInfo = mediaInfo
        self.videoFrameBufferQueue = Queue(self.vQueueSize)
        self.audioFrameBufferQueue = Queue( self.aQueueSize)
        self.srFrameBufferQueue = None
        self.videoDecodeThread = None
        self.audioDecodeThread = None
        self.videoPlayThread = None
        self.audioPlayThread = None
        self.videoDecodeWorker = None
        self.audioDecodeWorker = None
        self.videoPlayWorker = None
        self.audioPlayWorker = None
        self.videoContextList = None
        self.audioContextList = None
        self.updatePlaybackProgressTimerThread = None
        self.updatePlaybackProgressTimer = None
        self.play_pause_signal.connect(self.pause)
        self.play_resume_signal.connect(self.resume)
        self.curr_slice_index = 0
        self.curr_slice_frame_rate = None
        self.max_slice = 0
        self.play_clock = PlayClock()
        self.playback_progress = 0.0
        self.durationTime = 0.0
        self.lastDurationTime = 0.0
        self.sliceDurationTimeList = None

        self.sr_mode = False
        # self.play_clock.upadte_progress.connect(self.update_progress)

        self.bufferLocker = QMutex()
        self.aBufferLocker = QMutex()
        self.audioBufferStatus = False
        self.vBufferLocker = QMutex()
        self.videoBufferStatus = False

        self.playStatus = True
        self.playEndStatus = False
        self.playStatusController = PlayStatusController()
        self.playStatusController.update_status.connect(self.play_wait_buffer_slot)
        # self.videoStatusNeuron = BinaryNeuron(True)
        # self.audioStatusNeuron = BinaryNeuron(True)
        # self.playStatusNeuron = BinaryNeuron(True)
        self.playEndStatusNeuron = BinaryNeuron(True)
        # self.videoStatusNeuron.outStatus.connect(self.playStatusNeuron.inOne)
        # self.audioStatusNeuron.outStatus.connect(self.playStatusNeuron.inTwo)
        # self.playStatusNeuron.outStatus.connect(self.play_wait_buffer_slot)
        self.playEndStatusNeuron.outStatus.connect(self.check_play_end)
        self.exceptionStatus = False

        self.inited = True

    def play(self, mediaInfo:MediaInfo):
        # print("play is {}".format(QThread.currentThreadId()))  
        if not self.isFirstLoad:
            self.cleanUp()
        else:
            self.isFirstLoad = False
        try:
            self.init(mediaInfo)
            self.init_avContext(mediaInfo)
            self.send_duration_time.emit(round(self.durationTime))
            self.init_avPlayWorker()
            # if self.enable_rtsr:
            #     self.init_rtstWorker()
            self.play_slice(self.curr_slice_index, 0,0, self.sr_mode,sr_context=self.srContext)
        except Exception as e:
            LOGGER.error(e.with_traceback())
            self.shutdown()


            

    def init_avContext(self, mediaInfo:MediaInfo):
        LOGGER.info("init AVContext")
        vlen = len(mediaInfo.video_url)
        alen = len(mediaInfo.audio_url)

        if vlen!=alen:
            self.exceptionStatus = True
            self.media_info_exception_signal.emit("视频源与音频源数量不匹配!")
            LOGGER.error("视频源与音频源数量不匹配!")
            return 
            # raise ValueError("视频源与音频源数量不匹配!")

        if vlen == 0:
            self.exceptionStatus = True
            self.media_info_exception_signal.emit("没有音视频源!")
            LOGGER.error("没有音视频源!")
            return
            # raise ValueError("没有音视频源!")

        self.max_slice = vlen

        self.videoContextList=[]
        self.audioContextList=[]
        self.sliceDurationTimeList = []

        for i in range(vlen):
            try:
                videoContext = VideoContext(
                                            url=mediaInfo.video_url[i],
                                            source=mediaInfo.source,
                                            req_method=mediaInfo.req_method,
                                            req_header=mediaInfo.req_header,
                                            req_params=mediaInfo.req_params,
                                            req_data=mediaInfo.req_data
                                            )
                # videoContext.frame_rate=24
                self.videoContextList.append(videoContext)
            except:
                self.exceptionStatus = True
                self.get_AVContext_failed.emit("Get VideoContext failed")
                LOGGER.error("Get VideoContext failed")
            try:
                audioContext = AudioContext(
                                            url=mediaInfo.audio_url[i],
                                            source=mediaInfo.source,
                                            req_method=mediaInfo.req_method,
                                            req_header=mediaInfo.req_header,
                                            req_params=mediaInfo.req_params,
                                            req_data=mediaInfo.req_data
                                            )
                audioContext.frame_rate = videoContext.frame_rate
                self.durationTime += audioContext.duration
                self.sliceDurationTimeList.append(audioContext.duration)
                self.audioContextList.append(audioContext)
                
            except:
                self.get_AVContext_failed.emit("AudioContext init failed")
                LOGGER.error("AudioContext init failed")


    def init_avPlayWorker(self):
        LOGGER.debug("init AVPlayWorker")
        self.videoPlayThread = QThread()
        self.videoPlayWorker = VideoPlayWorker(self.videoDevice,self.videoFrameBufferQueue,self.play_clock)
        self.videoPlayWorker.moveToThread(self.videoPlayThread)
        # self.videoPlayWorker.wait_buffer_signal.connect(self.videoStatusNeuron.inOne)
        self.videoPlayWorker.wait_buffer_signal.connect(self.playStatusController.video_wait_buffer_slot)
        self.videoPlayWorker.quit_signal.connect(self.playEndStatusNeuron.inOne)
        self.videoPlayThread.started.connect(self.videoPlayWorker.play)

        self.audioPlayThread = QThread()
        self.audioPlayWorker = AudioPlayWorker(self.audioDevice,self.audioFrameBufferQueue,self.play_clock)
        self.audioPlayWorker.moveToThread(self.audioPlayThread)
        # self.audioPlayWorker.wait_buffer_signal.connect(self.audioStatusNeuron.inOne)
        self.audioPlayWorker.wait_buffer_signal.connect(self.playStatusController.audio_wait_buffer_slot)
        self.audioPlayWorker.quit_signal.connect(self.playEndStatusNeuron.inTwo)
        self.audioPlayThread.started.connect(self.audioPlayWorker.play)

        self.videoPlayThread.start()
        self.audioPlayThread.start()

    def init_rtstWorker(self,srContext:SRContext):
        self.srFrameBufferQueue = Queue(self.vQueueSize)
        self.rtsrThread = QThread()
        self.rtsrWorker = RTSRWorker(srContext,self.videoFrameBufferQueue,self.srFrameBufferQueue)
        self.rtsrWorker.moveToThread(self.rtsrThread)
        self.rtsrThread.started.connect(self.rtsrWorker.work)
        self.rtsrThread.start()

    def play_slice(self, slice_index:int, ss:int, base_pts:int=0, sr_mode:bool=False, sr_context:SRContext=None):
        # LOGGER.info("playLocker locked")
        # print("play_slice is {}".format(QThread.currentThreadId()))  

        # if sr_mode:
        #     vcontext:VideoContext = self.videoContextList[slice_index]
        #     # self.videoDevice.setup([vcontext.frame_width*4,vcontext.frame_height*4])
        #     self.videoDevice.setup_signal.emit([vcontext.frame_width*4,vcontext.frame_height*4])
        #     # self.videoDevice.setup_signal.emit([1920,1080])
        #     self.videoDevice.playOnCuda()

        self.init_slice(slice_index,ss,base_pts,sr_mode,sr_context)
        self.updatePlaybackProgressTimerThread = QThread()
        self.updatePlaybackProgressTimer = QTimer()
        self.updatePlaybackProgressTimer.setInterval(500)
        self.updatePlaybackProgressTimer.moveToThread(self.updatePlaybackProgressTimerThread)
        self.updatePlaybackProgressTimer.timeout.connect(self.update_progress)
        self.updatePlaybackProgressTimerThread.started.connect(self.updatePlaybackProgressTimer.start)
        self.updatePlaybackProgressTimerThread.finished.connect(self.updatePlaybackProgressTimer.stop)
        # self.resume()
        self.updatePlaybackProgressTimerThread.start()
        




    def init_slice(self, slice_index:int, ss:int, base_pts:int=0, sr_mode:bool=False, sr_context:SRContext=None):
        if self.videoContextList is not None:
            self.videoPlayWorker.set_frame_rate.emit(self.videoContextList[slice_index].frame_rate)
            self.vdecode_worker_init(self.videoContextList[slice_index],ss,base_pts,sr_mode,sr_context)

        if self.audioContextList is not None:
            self.audioPlayWorker.set_frame_rate.emit(self.audioContextList[slice_index].frame_rate)
            self.adecode_worker_init(self.audioContextList[slice_index],ss,base_pts)

        if self.videoContextList is not None:
            # self.videoPlayThread.start()
            self.videoDecodeThread.start()
            LOGGER.info("VDecodeThread started")

        if self.audioContextList is not None:
            # self.audioPlayThread.start()
            self.audioDecodeThread.start()
            LOGGER.info("ADecodeThread started")
        # self.avPlayThread.start()

    def vdecode_worker_init(self,vContext:VideoContext, ss:int=0, base_pts:int=0, sr_mode:bool=False, sr_context:SRContext=None):
        LOGGER.info("run vdecode_worker_init")
        self.videoDecodeThread = QThread()
        self.videoDecodeWorker = VideoDecodeWorker(vContext, self.videoFrameBufferQueue, ss,base_pts,sr_mode,sr_context)
        self.videoDecodeWorker.moveToThread(self.videoDecodeThread)
        # self.videoDecodeWorker.buffer_queue_full_signal.connect(self.videoStatusNeuron.inTwo)
        self.videoDecodeWorker.buffer_queue_full_signal.connect(self.playStatusController.video_buffer_full_slot)
        self.videoDecodeThread.started.connect(self.videoDecodeWorker.work)

    def adecode_worker_init(self, aContext:AudioContext, ss:int=0, base_pts:int=0):
        LOGGER.info("run adecode_worker_init")
        self.audioDecodeThread = QThread() 
        self.audioDecodeWorker = AudioDecodeWorker(aContext,self.audioFrameBufferQueue,ss,base_pts)
        self.audioDecodeWorker.moveToThread(self.audioDecodeThread)
        # self.audioDecodeWorker.buffer_queue_full_signal.connect(self.audioStatusNeuron.inTwo)
        self.audioDecodeWorker.buffer_queue_full_signal.connect(self.playStatusController.audio_buffer_full_slot)
        self.audioDecodeWorker.decode_end_signal.connect(self.decode_next_slice)
        self.audioDecodeThread.started.connect(self.audioDecodeWorker.work)

    def play_wait_buffer_slot(self,status:bool):
        if status:
            LOGGER.debug("buffer ok")
            self.resume()
            self.buffer_ok_signal.emit()
        else:
            LOGGER.debug("wait buffer")
            self.pause()
            self.wait_buffer_signal.emit()


    def update_progress(self,):
        # print(round(self.play_clock.curr_ts))
        self.update_playback_progress.emit(round(self.play_clock.curr_ts))

    def decode_next_slice(self,):
        LOGGER.info("The slice {} is completed".format(self.curr_slice_index))
        self.curr_slice_index += 1
        if self.curr_slice_index < self.max_slice:
            # self.wait_buffer_signal.emit()
            self.quit_timer()
            self.quit_avdecode()
            self.playStatusController.wait_buffer_mode()
            self.lastDurationTime += self.sliceDurationTimeList[self.curr_slice_index-1]
            self.videoPlayWorker.frame_last_pts = self.lastDurationTime 
            self.play_clock.curr_ts = self.lastDurationTime
            self.play_slice(self.curr_slice_index, 0,self.lastDurationTime,self.sr_mode,sr_context=self.srContext)
        else:
            
            # 发送退出信号，播放完成后退出
            # self.quit_avplay_worker()
            self.quit_timer()
            self.quit_avdecode()
            # self.shutdown()
            

    def check_play_end(self,status:bool):
        if status:
            self.playEndStatus = True
            LOGGER.info("Paly end")
            self.play_end_signal.emit()

    def replay(self,):
        self.curr_slice_index = 0
        # self.videoStatusNeuron.reset()
        # self.audioStatusNeuron.reset()
        # self.playStatusNeuron.reset()
        self.playStatusController = PlayStatusController()
        self.playEndStatusNeuron.reset()
        self.playStatus = True
        self.playEndStatus = False
        self.play_clock = PlayClock()
        self.init_avPlayWorker()
        self.play_slice(self.curr_slice_index, 0,sr_context=self.srContext)

            


    def vdcoder_init_status_slot(self,statusCode:int):
        pass

    def adcoder_init_status_slot(self,statusCode:int):
        pass

    # def clear_vbuffer(self):
    #     self.videoFrameBufferQueue = Queue(self.vQueueSize)
    #     self.videoDecodeWorker.buffer_queue = self.videoFrameBufferQueue
    #     self.videoPlayWorker.buffer_queue = self.videoFrameBufferQueue

    # def clear_abuffer(self):
    #     self.audioFrameBufferQueue = Queue(self.aQueueSize)
    #     self.audioDecodeWorker.buffer_queue = self.audioFrameBufferQueue
    #     self.audioPlayWorker.buffer_queue = self.audioFrameBufferQueue

    def resume(self,):
        
        # if not self.playStatus and not self.playEndStatus:
            # self.playStatus = True
        if not self.playEndStatus:
            LOGGER.debug("paly resume")
            if self.videoPlayWorker is not None:
                self.videoPlayWorker.resume_signal.emit()
            if self.audioPlayWorker is not None:
                self.audioPlayWorker.resume_signal.emit()

    def pause(self,):
        # if self.playStatus and not self.playEndStatus:
        #     self.playStatus = False
        if not self.playEndStatus:
            LOGGER.debug("paly pause")
            if self.audioPlayWorker is not None:
                self.audioPlayWorker.pause_signal.emit()
            if self.videoPlayWorker is not None:
                self.videoPlayWorker.pause_signal.emit()

    def seek(self,ss:int,):
        # self.wait_buffer_signal.emit()
        self.quit_timer()
        self.quit_avdecode()
        # self.playEndStatusNeuron.reset()

        # self.pause()
        self.playStatusController.wait_buffer_mode()
        slice_index, ts = self.convert2slice_ts(ss)
        if slice_index == -1:
            raise ValueError("seek超出时长范围!")
        if slice_index > 0:
            self.lastDurationTime = 0 
            for i in range(slice_index):
                self.lastDurationTime += self.sliceDurationTimeList[i]
        else:
            self.lastDurationTime = 0
        self.curr_slice_index = slice_index
        self.videoPlayWorker.frame_last_pts = ss 
        self.play_clock.curr_ts = ss
        
        self.play_slice(slice_index, ts, self.lastDurationTime,self.sr_mode,sr_context=self.srContext)

    def switchSRMode(self,state:bool):
        if state:
            self.enableSR()
        else:
            self.disableSR()

    def enableSR(self,):
        # assert self.srContext is not None
        self.sr_mode = True
        self.seek(self.play_clock.curr_ts)
    
    def disableSR(self):
        self.sr_mode = False
        self.seek(self.play_clock.curr_ts)


    def convert2slice_ts(self,ss:int):
        s = 0
        index = 0
        ts = 0
        for idx, t in enumerate(self.sliceDurationTimeList):
            index = idx
            s += t
            if ss <= round(s):
                ts = self.sliceDurationTimeList[index] - (s - ss)
                break
            if ss>round(s) and index+1 == len(self.sliceDurationTimeList):
                index =-1
                break
        return index, ts

    def quit_avdecode(self):
        self.quit_avdecode_worker()
        self.clear_avbuffer()
        self.quit_avdecode_thread()
        
    def clear_avbuffer(self):
        while not self.videoFrameBufferQueue.empty():
            try:
                self.videoFrameBufferQueue.get_nowait()
            except:
                break
        
        while not self.audioFrameBufferQueue.empty():
            try:
                self.audioFrameBufferQueue.get_nowait()
            except:
                break

    def quit_avdecode_worker(self):
        if self.videoDecodeWorker is not None:
            LOGGER.debug("quit video decode worker")
            self.videoDecodeWorker.quit()
            self.videoDecodeWorker = None

        if self.audioDecodeWorker is not None:
            LOGGER.debug("quit audio decode worker")
            self.audioDecodeWorker.quit()
            self.audioDecodeWorker = None

    def quit_avdecode_thread(self):
        if self.videoDecodeThread is not None:
            LOGGER.debug("quit video decode thread")
            self.videoDecodeThread.quit()
            self.videoDecodeThread.wait()
            # self.videoDecodeThread.terminate()
            self.videoDecodeThread = None

        if self.audioDecodeThread is not None:
            LOGGER.debug("quit audio decode thread")
            self.audioDecodeThread.quit()
            self.audioDecodeThread.wait()
            # self.audioDecodeThread.terminate()
            self.audioDecodeThread = None

    def quit_avplay_worker(self,force:bool=False):
        if self.videoPlayWorker is not None:
            LOGGER.debug("quit video play worker")
            if True:
                self.videoPlayWorker.forcedQuit()
            else:
                self.videoPlayWorker.quit()
            self.videoPlayWorker = None

        if self.audioPlayWorker is not None:
            LOGGER.debug("quit audio play worker")
            if force:
                self.audioPlayWorker.forcedQuit()
            else:
                self.audioPlayWorker.quit()
            self.audioPlayWorker = None


    def quit_avplay_thread(self):
        if self.videoDecodeThread is not None:
            LOGGER.debug("quit video play thread")
            self.videoPlayThread.quit()
            self.videoPlayThread.wait()
            self.videoPlayThread = None

        if self.audioDecodeThread is not None:
            LOGGER.debug("quit audio play thread")
            self.audioPlayThread.quit()
            self.audioPlayThread.wait()
            self.audioPlayThread = None


    def shutdown(self,force:bool=False):
        # if self.updatePlaybackProgressTimer is not None:
        #     self.updatePlaybackProgressTimer.stop()
        if not self.inited:
            return
        self.quit_timer()
        self.quit_avplay_worker(force)
        self.quit_avdecode()
        self.quit_avplay_thread()
        # self.resume()


    def quit_timer(self):
        if self.updatePlaybackProgressTimerThread is not None:
            self.updatePlaybackProgressTimerThread.quit()
            self.updatePlaybackProgressTimerThread.wait()
            self.updatePlaybackProgressTimer = None

    
    def cleanUp(self):
        # 手动清理部分占内存的变量
        if self.audioFrameBufferQueue is not None:
            del self.audioFrameBufferQueue
        if self.videoFrameBufferQueue is not None:
            del self.videoFrameBufferQueue
        if self.videoContextList is not None:
            del self.videoContextList
        if self.audioContextList is not None:
            del self.audioContextList
