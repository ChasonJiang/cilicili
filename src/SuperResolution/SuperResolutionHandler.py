import json
import logging
from multiprocessing.connection import PipeConnection
import os
# from queue import 
import sys
from threading import Thread
from time import sleep
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from multiprocessing import Pipe, Process, Queue
from .ClassLoader import classLoader

from .VideoDecoder import VideoDecoder
from .SRContext import SRContext
from .SRStatusCode import SRStatusCode as SRSC
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
        self.videoDecoder = None
        self.inferencerInfo = None
        self.inferencer = None
        self.frameBufferQueue = None

    
    def init(self):
        
        self.loadInferencerInfo()
        self.loadInferencer(self.inferencerInfo["Inferencer"][self.inferencerInfo["Default"]]["ClassName"],
                            self.inferencerInfo["Inferencer"][self.inferencerInfo["Default"]]["ClassPath"]
                            )

    def run(self):
        print("Running SuperResolutionHandler")
        self.init()
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
                decoderContext = handlerCmd.args
                self.frameBufferQueue = Queue(10)
                sr_mode:bool = decoderContext["sr_mode"]

                if sr_mode:
                    self.srWorker = SRWorker( self.frameBufferQueue, self.inferencer, self.srContext)
                    self.srWorker.setDaemon(True)
                    self.srWorker.start()

                self.videoDecoder = VideoDecoder(decoderContext, self.srContext, self.frameBufferQueue if sr_mode else None)
                self.videoDecoder.setDaemon(True)
                self.videoDecoder.start()
                
            elif handlerCmd.cmd == HandlerCmd.QuitSRWorker:
                # self.quitEventLoop()
                self.quitVideoDecoder()
                self.quitSRWorker()
                self.clearFrameBuffer()
                continue
            elif handlerCmd.cmd == HandlerCmd.QuitSRThread:
                
                # self.quitSRThread()
                continue

    def clearFrameBuffer(self):
        if self.frameBufferQueue is not None:
            while not self.frameBufferQueue.empty():
                self.frameBufferQueue.get_nowait()


    def quitVideoDecoder(self):
        # print("Quit Inferencer")
        if self.videoDecoder is not None:
            print("quit videoDecoder")
            self.videoDecoder.quit()

    def quitSRWorker(self):
        # print("Quit Inferencer")
        if self.srWorker is not None:
            print("quit srWorker")
            self.srWorker.quit()

    def loadInferencerInfo(self):
        print("Load Inferencer Info")
        try:
            with open(os.path.join(os.path.dirname(__file__),"SuperResolutionInferencer","SuperResolutionInferencerRegister.json"),"r") as f:
                self.inferencerInfo = json.loads(f.read())
        except IOError:
            print("Error reading SuperResolutionInferencerRegister.json")
            LOGGER.error("Error reading SuperResolutionInferencerRegister.json")
            self.srContext.msgPipe.send(SRSC.LoadInferencerInfoFailed)
            raise RuntimeError("Load InferencerInfo Failed")
            # LOGGER.error(os.path.join(os.path.dirname(__file__),"SuperResolutionInferencer","SuperResolutionInferencerRegister.json"))
            
    def loadInferencer(self,className:str, classPath:str):
        print("Load Inferencer")
        try:
            inferencer:Inferencer = classLoader("SuperResolution.SuperResolutionInferencer."+classPath,className)
            self.inferencer = inferencer()
        except:
            print("LoadInferencer Error")
            LOGGER.error("LoadInferencer Error")
            self.srContext.msgPipe.send(SRSC.LoadInferencerFailed)
            raise RuntimeError("Load Inferencer Failed")
        
    # def loadInferencer(self,className:str, classPath:str):
    #     try:
    #         inferencer:Inferencer =classloader("SuperResolution.SuperResolutionInferencer."+classPath,className)
    #     except:
    #         print("LoadInferencer Error")
    #         LOGGER.error("LoadInferencer Error")
    #         self.srContext.msgPipe.send(SRSC.LoadInferencerError)

    #     return inferencer()






