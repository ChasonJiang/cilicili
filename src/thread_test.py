import sys
from time import sleep
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import ffmpeg
import cv2
import numpy as np


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
        counter=0
        while True:
            if self.obj is not None:
                self.obj.update("{}: in chunk: {} ".format(self.name,counter))
            
            sleep(0.5)


    
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
                # print("{}: in chunk: {} ".format(self.name,counter))
                if self.obj is not None:
                    self.obj.update("{}: in chunk: {} ".format(self.name,counter))
                if not in_bytes:
                    break
                in_frame = (
                    np
                    .frombuffer(in_bytes, np.uint8)
                    .reshape([1080, 1920, 3])
                )
                cv2.imwrite("./test/{}.png".format(counter),in_frame)
        except:
            print("exception")


class SWorker(QObject):
    signal = pyqtSignal()
    msg_a = pyqtSignal(str)
    msg_b = pyqtSignal(str)
    msg_c = pyqtSignal(str)
    msg_d = pyqtSignal(str)
    send_msg_signal = pyqtSignal(str)
    def __init__(self,name,func,obj):
        super(SWorker,self).__init__()
        print("Init Thread {}".format(name))
        print("{}: {}".format(name,QThread.currentThreadId()))
        self.name =name
        self.send_msg_signal.connect(self.send_msg)
        self.func = func
        self.obj= obj
    
    def receive_msg(self, msg):
        print("Thread {} receive {}".format(self.name,msg))

    def work(self, msg):
        print(msg)
        print("SWorker is running")
        self.work_init()
        # self.b.doWork_signal.emit("asdkfjaskldjhfklj")
        # self.b.signal.emit()
        # self.b.change_name_signal.emit("aksjdfksjd")
        print("SWorker end of work")

    def work_init(self):
        self.at = QThread()
        self.bt = QThread()
        self.a = Worker("A",self.func,self.obj)
        self.b = Worker("B",self.func,self.obj)
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
        self.c = WorkerB("C",self.func,self.obj)
        self.d = WorkerB("D",self.func,self.obj)
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
        self.messager = Messager()

    def run(self):
        self.s = SWorker("S",self.receive_msg,self.messager)
        self.st= QThread()
        self.s.moveToThread(self.st)
        self.s.signal.connect(self.s.work)
        self.msg_s.connect(self.s.send_msg)
        # self.s.send_msg_signal.connect(self.s.send_msg)
        # self.st.started.connect(lambda: self.s.signal.emit())
        self.st.started.connect(lambda:self.s.work("asldjfhlkaisdhflasdkhjflaksjhfk"))
        self.st.start()

    def receive_msg(self, msg):
        print("Main thread receive {}".format(msg))


    def mousePressEvent(self, event):
        print("mousePressEvent from Window")
        self.msg_s.emit("a msg from msg_s")
        self.s.send_msg_signal.emit("a msg from s.send_msg_signal")
        return super().mousePressEvent(event)
        

if __name__ =="__main__":
    app = QApplication(sys.argv)
    w=Window()
    w.show()
    w.run()
    sys.exit(app.exec_())