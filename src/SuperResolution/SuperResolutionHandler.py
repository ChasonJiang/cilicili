import json
import logging
from multiprocessing.connection import PipeConnection
import os
from time import sleep
from PyQt5.QtCore import *
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
        self.superResolutionInferencer = None
        self.srThread = None
        self.srWorker = None
        # print(os.path.join(os.path.dirname(__file__),"SuperResolutionInferencer","SuperResolutionInferencerRegister.json"))
        try:
            with open(os.path.join(os.path.dirname(__file__),"SuperResolutionInferencer","SuperResolutionInferencerRegister.json"),"r") as f:
                self.superResolutionInferencer = json.loads(f.read())
        except IOError:
            LOGGER.error("Error reading SuperResolutionInferencerRegister.json")
            # LOGGER.error(os.path.join(os.path.dirname(__file__),"SuperResolutionInferencer","SuperResolutionInferencerRegister.json"))
            self.srContext.msgPipe.send(SRSC.IoError)
        # print(self.superResolutionInferencer)


    def run(self):
        while True:
            # print("polling from SuperResolutionHandler")
            # if self.inCmdPipe.poll():
            # print("recving")
            handlerCmd:HandlerCmd =  self.srContext.msgPipe.recv() 
            if handlerCmd.cmd == HandlerCmd.Quit:
                self.quitThread()
                break
            elif handlerCmd.cmd == HandlerCmd.Start:
                inferencer = None
                if handlerCmd.args == None:
                    inferencer = self.loadInferencer(
                        self.superResolutionInferencer["SuperResolutionInferencer"]["default"]["ClassName"],
                        self.superResolutionInferencer["SuperResolutionInferencer"]["default"]["ClassPath"]
                        )
                else:
                    inferencer = self.loadInferencer(
                            self.superResolutionInferencer["SuperResolutionInferencer"][handlerCmd.args]["ClassName"],
                            self.superResolutionInferencer["SuperResolutionInferencer"][handlerCmd.args]["ClassPath"]
                            )
                self.srWorker = SRWorker(inferencer,self.srContext.inputDataPipe, self.srContext.outputDataPipe)
                self.srThread = QThread()
                self.srWorker.moveToThread(self.srThread)
                self.srThread.started.connect(self.srWorker.inference)
                self.srThread.finished.connect(self.srWorker.quit)
                self.srThread.start()
                self.srContext.outputDataPipe.send(SRSC.InferencerStarted)

    

    def quitThread(self):
        # if self.srWorker is not None:
        #     self.srWorker.quit()
        if self.srThread is not None:
            self.srThread.quit()
            self.srThread.wait()


    def loadInferencer(self,className:str, classPath:str):
        try:
            inferencer:Inferencer =classloader("SuperResolution.SuperResolutionInferencer."+classPath,className)
        except:
            print("LoadInferencer Error")
            LOGGER.error("LoadInferencer Error")
            self.srContext.msgPipe.send(SRSC.LoadInferencerError)

        return inferencer()






