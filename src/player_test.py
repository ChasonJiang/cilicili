import logging
from queue import Queue
import sys
from time import sleep
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import ffmpeg
import cv2
import numpy as np

from player.DisplayLayer import DisplayLayer
from player.utils.AudioDecodeWorker import AudioDecodeWorker
from player.utils.AudioDevice import AudioDevice
from player.utils.AudioPlayWorker import AudioPlayWorker
from player.utils.MediaInfo import MediaInfo
from player.utils.PlayWorker import PlayWorker
from player.utils.VideoContext import VideoContext
from player.utils.VideoDecodeWorker import VideoDecodeWorker
from player.utils.AudioContext import AudioContext
from player.utils.VideoPlayWorker import VideoPlayWorker
logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO) # DEBUG
LOGGER=logging.getLogger("PlayWorker")

class WorkerA(QObject):
    def __init__(self, ):
        super(WorkerA, self).__init__()
        # LOGGER.info("init VideoDecodeWorker")

        self.name = "VideoDecodeWorker"
        self.process=None

    def work(self):
        # self.run_init()
        # self.run()
        print("Thread {} is working".format(self.name))
        print("My name is {}".format(self.name))
        #     sleep(0.5)
        name=np.random.rand()
        self.process = (
                ffmpeg
                .input('assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv',thread_queue_size="8",loglevel="quiet")
                .output("-" , format='s16le', ac="2", ar="48000")
                .run_async(pipe_stdout=True)
            )
        counter=0
        try:
            while True:
                counter+=1
                # continue
                in_bytes = self.process.stdout.read(1920 * 1080 * 3)
                # in_bytes = proc.stdout.read(1024*1024*1024)
                # self.send_msg_signal.emit("{}: in chunk: {} ".format(self.name,counter))
                # self.func("{}: in chunk: {} ".format(self.name,counter))
                print("{}: in chunk: {} ".format(name,counter))
                # if self.obj is not None:
                #     self.obj.update("{}: in chunk: {} ".format(self.name,counter))
                if not in_bytes:
                    break
                in_frame = (
                    np
                    .frombuffer(in_bytes, np.uint8)
                    .reshape([1080, 1920, 3])
                )
                sleep(0.1)
                # cv2.imwrite("./test/{}.png".format(counter),in_frame)
        except:
            print("exception")
        





class WorkerB(QObject):
    signal = pyqtSignal()
    do_work = pyqtSignal()
    doWork = pyqtSignal()
    change_name_signal = pyqtSignal(str)
    receive_msg_signal = pyqtSignal(str)
    send_msg_signal = pyqtSignal(str)
    def __init__(self,name,func,obj=None):
        super(WorkerB,self).__init__()
        print("Init Thread {}".format(name))
        print("{}: {}".format(name,QThread.currentThreadId()))
        self.name = name
        self.do_work.connect(self.work)
        self.doWork.connect(self.work)
        self.receive_msg_signal.connect(self.receive_msg)
        self.process = None
        self.func = func
        self.obj= obj

    def receive_msg(self, msg):
        print("Thread {} receive {}".format(self.name,msg))

    def change_name(self,name:str):
        print("run change_name")
        self.name = name
        self.doWork.emit()
        print("end")

    def work(self):
        # self.run_init()
        # self.run()
        print("Thread {} is working".format(self.name))
        print("My name is {}".format(self.name))
        #     sleep(0.5)

        self.process = (
                ffmpeg
                .input('assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv',thread_queue_size="8",loglevel="quiet")
                .output("-" , format='s16le', ac="2", ar="48000")
                .run_async(pipe_stdout=True)
            )
        counter=0
        try:
            while True:
                counter+=1
                # continue
                in_bytes = self.process.stdout.read(1920 * 1080 * 3)
                # in_bytes = proc.stdout.read(1024*1024*1024)
                # self.send_msg_signal.emit("{}: in chunk: {} ".format(self.name,counter))
                # self.func("{}: in chunk: {} ".format(self.name,counter))
                print("{}: in chunk: {} ".format(self.name,counter))
                # if self.obj is not None:
                #     self.obj.update("{}: in chunk: {} ".format(self.name,counter))
                if not in_bytes:
                    break
                in_frame = (
                    np
                    .frombuffer(in_bytes, np.uint8)
                    .reshape([1080, 1920, 3])
                )
                sleep(0.1)
                # cv2.imwrite("./test/{}.png".format(counter),in_frame)
        except:
            print("exception")

    
    # def run_init(self):
    #     v = np.random.rand()
    #     if v >0.5:
    #         self.process = (
    #             ffmpeg
    #             .input('assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv',thread_queue_size="8",loglevel="quiet")
    #             .output("-" , format='rawvideo', pix_fmt='rgb24')
    #             .run_async(pipe_stdout=True)
    #         )
    #     else:
    #         self.process = (
    #             ffmpeg
    #             .input('assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv',thread_queue_size="8",loglevel="quiet")
    #             .output("-" , format='s16le', ac="2", ar="48000")
    #             .run_async(pipe_stdout=True)
    #         )




class Worker(QObject):
    signal = pyqtSignal()
    do_work = pyqtSignal()
    doWork = pyqtSignal()
    change_name_signal = pyqtSignal(str)
    receive_msg_signal = pyqtSignal(str)
    send_msg_signal = pyqtSignal(str)
    def __init__(self,name,func,obj=None):
        super(Worker,self).__init__()
        print("Init Thread {}".format(name))
        print("{}: {}".format(name,QThread.currentThreadId()))
        self.name = name
        self.do_work.connect(self.work)
        self.doWork.connect(self.work)
        self.receive_msg_signal.connect(self.receive_msg)
        self.process = None
        self.func = func
        self.obj= obj

    def receive_msg(self, msg):
        print("Thread {} receive {}".format(self.name,msg))

    def change_name(self,name:str):
        print("run change_name")
        self.name = name
        self.doWork.emit()
        print("end")

    def work(self):
        self.run_init()
        self.run()
    
    def run_init(self):
        v = np.random.rand()
        if v >0.5:
            self.process = (
                ffmpeg
                .input('assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv',thread_queue_size="8",loglevel="quiet")
                .output("-" , format='rawvideo', pix_fmt='rgb24')
                .run_async(pipe_stdout=True)
            )
        else:
            self.process = (
                ffmpeg
                .input('assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv',thread_queue_size="8",loglevel="quiet")
                .output("-" , format='s16le', ac="2", ar="48000")
                .run_async(pipe_stdout=True)
            )


    def run(self):

        # while True:
        print("Thread {} is working".format(self.name))
        print("My name is {}".format(self.name))
        #     sleep(0.5)
        counter=0
        try:
            while True:
                counter+=1
                # continue
                in_bytes = self.process.stdout.read(1920 * 1080 * 3)
                # in_bytes = proc.stdout.read(1024*1024*1024)
                # self.send_msg_signal.emit("{}: in chunk: {} ".format(self.name,counter))
                # self.func("{}: in chunk: {} ".format(self.name,counter))
                print("{}: in chunk: {} ".format(self.name,counter))
                # if self.obj is not None:
                #     self.obj.update("{}: in chunk: {} ".format(self.name,counter))
                if not in_bytes:
                    break
                in_frame = (
                    np
                    .frombuffer(in_bytes, np.uint8)
                    .reshape([1080, 1920, 3])
                )
                sleep(0.1)
                # cv2.imwrite("./test/{}.png".format(counter),in_frame)
        except:
            print("exception")

videoFrameBufferQueue = Queue(10)
audioFrameBufferQueue = Queue(10)

class SWorker(QObject):
    signal = pyqtSignal()
    msg_a = pyqtSignal(str)
    msg_b = pyqtSignal(str)
    msg_c = pyqtSignal(str)
    msg_d = pyqtSignal(str)
    send_msg_signal = pyqtSignal(str)
    play_pause_signal = pyqtSignal()
    play_resume_signal = pyqtSignal()
    def __init__(self,name,func,obj,videoDevice, audioDevice, vQueueSize=10,aQueueSize=10):
        super(SWorker,self).__init__()
        print("Init Thread {}".format(name))
        print("{}: {}".format(name,QThread.currentThreadId()))
        self.name =name
        self.send_msg_signal.connect(self.send_msg)
        self.func = func
        self.obj= obj
        self.videoDevice = videoDevice
        self.audioDevice = audioDevice
        self.vQueueSize = vQueueSize
        self.aQueueSize = aQueueSize
        global videoFrameBufferQueue
        global audioFrameBufferQueue
        self.videoFrameBufferQueue = videoFrameBufferQueue
        self.audioFrameBufferQueue = audioFrameBufferQueue
        # self.videoDecodeThread = None
        # self.audioDecodeThread = None
        # self.videoPlayThread = None
        # self.audioPlayThread = None
        # self.videoDecodeWorker = None
        # self.audioDecodeWorker = None
        # self.videoPlayWorker = None
        # self.audioPlayWorker = None
        self.playMode = 0
        self.videoContextList = None
        self.audioContextList = None
        self.play_pause_signal.connect(self.pause)
        self.play_resume_signal.connect(self.resume)
        self.curr_slice_index = 0
        self.max_slice = 0

        self.bufferLocker = QMutex()
        self.aBufferLocker = QMutex()
        self.audioBufferStatus = False
        self.vBufferLocker = QMutex()
        self.videoBufferStatus = False
        self.playStatus = False


    def receive_msg(self, msg):
        print("Thread {} receive {}".format(self.name,msg))

    def work(self, mediaInfo):
        # print(msg)
        print("SWorker is running")
        self.work_init(mediaInfo)
        # self.b.doWork_signal.emit("asdkfjaskldjhfklj")
        # self.b.signal.emit()
        # self.b.change_name_signal.emit("aksjdfksjd")
        print("SWorker end of work")

    def work_init(self,mediaInfo):
        self.at = QThread()
        self.bt = QThread()
        self.a = WorkerB("A",self.func,self.obj)
        self.b = WorkerB("B",self.func,self.obj)
        self.a.signal.connect(self.a.work)
        self.msg_a.connect(self.a.receive_msg)
        self.a.send_msg_signal.connect(self.receive_msg)
        self.b.signal.connect(self.b.work)
        self.msg_b.connect(self.b.receive_msg)
        self.b.send_msg_signal.connect(self.receive_msg)
        self.a.moveToThread(self.at)
        self.b.moveToThread(self.bt)
        self.b.change_name_signal.connect(self.b.change_name)
        self.at.started.connect(self.a.work)
        # self.bt.started.connect(lambda:self.b.signal.emit())
        # self.bt.started.connect(lambda:self.b.do_work.emit())
        self.bt.started.connect(self.b.work)
        self.at.start()
        self.bt.start()

        self.ct = QThread()
        self.dt = QThread()
        self.c = Worker("C",self.func,self.obj)
        self.d = Worker("D",self.func,self.obj)
        self.c.signal.connect(self.c.work)
        self.c.send_msg_signal.connect(self.receive_msg)
        self.msg_c.connect(self.c.receive_msg)
        self.d.signal.connect(self.d.work)
        self.d.send_msg_signal.connect(self.receive_msg)
        self.msg_d.connect(self.d.receive_msg)
        self.c.moveToThread(self.ct)
        self.d.moveToThread(self.dt)
        self.d.change_name_signal.connect(self.d.change_name)
        self.ct.started.connect(self.c.work)
        # self.bt.started.connect(lambda:self.b.signal.emit())
        # self.bt.started.connect(lambda:self.b.do_work.emit())
        self.dt.started.connect(self.d.work)
        self.ct.start()
        self.dt.start()
        self.videoDecodeThread = QThread()
        self.audioDecodeThread = QThread() 
        self.videoDecodeWorker = WorkerA()
        self.audioDecodeWorker = WorkerA()


        self.videoDecodeWorker.moveToThread(self.videoDecodeThread)
        self.videoDecodeThread.started.connect(self.videoDecodeWorker.work)
        self.audioDecodeWorker.moveToThread(self.audioDecodeThread)
        self.audioDecodeThread.started.connect(self.audioDecodeWorker.work)
        self.videoDecodeThread.start()
        self.audioDecodeThread.start()

    # def play(self, mediaInfo:MediaInfo):
    #     # print("play is {}".format(QThread.currentThreadId()))  
    #     self.play_init(mediaInfo)
    #     self.play_slice(self.curr_slice_index, 0)

    # def play_init(self, mediaInfo:MediaInfo):
        LOGGER.info("init play")

        # while True:
        #     sleep(1) 
        self.mediaInfo = mediaInfo
        vlen = len(self.mediaInfo.video_url)
        alen = len(self.mediaInfo.audio_url)

        if vlen!=alen:
            raise ValueError("视频源与音频源不匹配!")

        if vlen == 0:
            raise ValueError("没有音视频源!")

        self.max_slice = vlen-1

        self.videoContextList=[]
        self.audioContextList=[]
        for i in range(vlen):
            if vlen>0:
                try:
                    videoContext = VideoContext(
                                                url=self.mediaInfo.video_url[i],
                                                source=self.mediaInfo.source,
                                                req_method=self.mediaInfo.req_method,
                                                req_header=self.mediaInfo.req_header,
                                                req_params=self.mediaInfo.req_params,
                                                req_data=self.mediaInfo.req_data
                                                )
                    self.videoContextList.append(videoContext)
                except:
                    raise RuntimeError("VideoContext init failed")
            if alen>0:
                try:
                    audioContext = AudioContext(
                                                url=self.mediaInfo.audio_url[i],
                                                source=self.mediaInfo.source,
                                                req_method=self.mediaInfo.req_method,
                                                req_header=self.mediaInfo.req_header,
                                                req_params=self.mediaInfo.req_params,
                                                req_data=self.mediaInfo.req_data
                                                )
                    audioContext.frame_rate = videoContext.frame_rate
                    self.audioContextList.append(audioContext)
                except:
                    raise RuntimeError("AudioContext init failed")
        # 初始化av PlayWorker线程
        # if vlen > 0:

        self.videoPlayThread = QThread()
        self.videoPlayWorker = VideoPlayWorker(self.videoDevice,self.videoFrameBufferQueue)
        # self.videoPlayWorker.wait_buffer_signal.connect(self.wait_buffer_slot)
        # self.videoPlayWorker.wait_buffer_signal.connect(self.v_wait_buffer_slot)
        self.videoPlayWorker.moveToThread(self.videoPlayThread)
        self.videoPlayThread.started.connect(self.videoPlayWorker.play)
        # self.videoPlayThread.finished.connect()
        # self.videoPlayThread.start()

        # if alen > 0:
        self.audioPlayThread = QThread()
        self.audioPlayWorker = AudioPlayWorker(self.audioDevice,self.audioFrameBufferQueue)
        # self.audioPlayWorker.wait_buffer_signal.connect(self.wait_buffer_slot)
        # self.audioPlayWorker.wait_buffer_signal.connect(self.a_wait_buffer_slot)
        self.audioPlayWorker.moveToThread(self.audioPlayThread)
        self.audioPlayThread.started.connect(self.audioPlayWorker.play)
        # self.audioPlayThread.start()
        # print("play_init is {}".format(QThread.currentThreadId()))  

    # def play_slice(self, slice_index:int, ss:int):
        # LOGGER.info("playLocker locked")
        # print("play_slice is {}".format(QThread.currentThreadId()))  


    def resume(self,):
        if not self.playStatus:
            print("paly resume")
            self.playStatus = True
            if self.videoPlayWorker is not None:
                self.videoPlayWorker.resume_signal.emit()
            if self.audioPlayWorker is not None:
                self.audioPlayWorker.resume_signal.emit()

    def pause(self,):
        if self.playStatus:
            print("paly pause")
            self.playStatus = False
            if self.audioPlayWorker is not None:
                self.audioPlayWorker.pause_signal.emit()
            if self.videoPlayWorker is not None:
                self.videoPlayWorker.pause_signal.emit()





    def send_msg(self, msg):
        print("SWorker is received the msg: {}".format(msg))
        self.msg_a.emit(msg)
        self.msg_b.emit(msg)
        self.a.receive_msg_signal.emit(msg+" from receive_msg_signal")
        self.b.receive_msg_signal.emit(msg+" from receive_msg_signal")


class Messager(QWidget):
    def __init__(self,):
        super(Messager, self).__init__()
    
    def update(self, msg):
        print(msg)


class Window(QWidget):
    msg_s = pyqtSignal(str)
    def __init__(self,parent=None):
        super(Window, self).__init__(parent=parent)
        # self.run()
        self.displayLayer=DisplayLayer(self)
        self.messager = Messager()
        self.audioDevice = AudioDevice()
        self.playStatus = True
        self.setupUi()

    def run(self,media_info):
        self.s = SWorker("S",self.receive_msg,self.messager,self.displayLayer,self.audioDevice)
        self.st= QThread()
        self.s.moveToThread(self.st)
        self.s.signal.connect(self.s.work)
        self.msg_s.connect(self.s.send_msg)
        # self.s.send_msg_signal.connect(self.s.send_msg)
        # self.st.started.connect(lambda: self.s.signal.emit())
        self.st.started.connect(lambda:self.s.work(media_info))
        self.st.start()

    def receive_msg(self, msg):
        print("Main thread receive {}".format(msg))


    def mousePressEvent(self, event):
        print("mousePressEvent from Window")
        self.msg_s.emit("a msg from msg_s")
        self.s.send_msg_signal.emit("a msg from s.send_msg_signal")
        self.playStatus = not self.playStatus
        if self.playStatus:
            print("emit play_resume_signal")
            # self.play_resume_signal.emit()
            self.s.play_resume_signal.emit()
            # self.playWorker.resume()
        else:
            print("emit play_pause_signal")
            # self.play_pause_signal.emit()
            self.s.play_pause_signal.emit()
        return super().mousePressEvent(event)


    def setupUi(self,):
        self.setWindowTitle("BasePlayer")
        self.setObjectName("BasePlayer")
        self.resize(1920,1080)
        self.setMinimumSize(1620,987)
        # 隐藏窗口边框
        # self.setWindowFlag(Qt.FramelessWindowHint, True)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        # self.displayLayer.setDisplayMode(16.0/9)
        self.layout.addWidget(self.displayLayer)

        # self.setGeometry(0,0,600,600

if __name__ =="__main__":
    media_info=MediaInfo(["assets\\5s.mkv", "assets\\5s.mkv"],["assets\\5s.mkv", "assets\\5s.mkv"],"file")
    app = QApplication(sys.argv)
    w=Window()
    w.show()
    w.run(media_info)
    sys.exit(app.exec_())