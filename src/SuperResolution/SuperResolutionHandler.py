import json
import logging
from multiprocessing.connection import PipeConnection
import os
import sys
from threading import Thread
from time import sleep
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from multiprocessing import Pipe, Process

from .SRContext import SRContext
from .SRStatusCode import SRStatusCode as SRSC
from .ClassLoader import classloader
from .SRWorker import SRWorker
from .Inferencer import Inferencer
from .HandlerCmd import HandlerCmd
# logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO) # DEBUG
LOGGER = logging.getLogger()

class SuperResolutionHandler(Process):

    def __init__(self, srContext):
        super(SuperResolutionHandler,self).__init__()
        assert isinstance(srContext,SRContext)
        # assert isinstance(errorPipe,PipeConnection)

        self.srContext = srContext
        self.srThread = None
        self.srWorker = None
        self.eventLoop = None


    def run(self):
        print("Running SuperResolutionHandler")
        while True:
            # print("polling from SuperResolutionHandler")
            # if self.inCmdPipe.poll():
            # print("recving")
            
            handlerCmd:HandlerCmd =  self.srContext.cmdPipe.recv() 
            # print(f"recving cmd: {handlerCmd.cmd} | args: {handlerCmd.args}")
            if handlerCmd.cmd == HandlerCmd.Quit:
                # self.quitSRWorker()
                break
            elif handlerCmd.cmd == HandlerCmd.Start:
                # self.quitEventLoop()
                # self.quitSRWorker()
                
                
                decoderContext = handlerCmd.args
                # sr = QApplication(sys.argv)
                self.srWorker = SRWorker(decoderContext,self.srContext)
                self.srWorker.setDaemon(True)
                self.srWorker.start()
                # self.srThread = QThread()
                # self.srWorker.moveToThread(self.srThread)
                # self.srThread.started.connect(self.srWorker.work)
                # self.srThread.finished.connect(self.srWorker.quit)
                # self.eventLoop = QEventLoop()
                # self.srThread.start()
                # sr.exec_()
                # self.eventLoop.exec()
                
            elif handlerCmd.cmd == HandlerCmd.QuitSRWorker:
                # self.quitEventLoop()
                self.quitSRWorker()
                continue
            elif handlerCmd.cmd == HandlerCmd.QuitSRThread:
                
                # self.quitSRThread()
                continue
    
    def quitEventLoop(self):
        if self.eventLoop is not None:
            self.eventLoop.quit()

    def quitSRWorker(self):
        # print("Quit Inferencer")
        if self.srWorker is not None:
            print("quit srWorker")
            self.srWorker.quit()
    def quitSRThread(self):
        if self.srThread is not None:
            print("quit srThread")
            self.srThread.quit()
            self.srThread.wait()
            print("wait finally")


    # def loadInferencer(self,className:str, classPath:str):
    #     try:
    #         inferencer:Inferencer =classloader("SuperResolution.SuperResolutionInferencer."+classPath,className)
    #     except:
    #         print("LoadInferencer Error")
    #         LOGGER.error("LoadInferencer Error")
    #         self.srContext.msgPipe.send(SRSC.LoadInferencerError)

    #     return inferencer()






