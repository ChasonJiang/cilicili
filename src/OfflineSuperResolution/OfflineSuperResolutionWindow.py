import json
import logging
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from OfflineSuperResolution.Worker.VideoEncodeWorker import VideoEncodeWorker
from VideoProcessor.HandlerCmd import HandlerCmd
from VideoProcessor.SRStatusCode import SRStatusCode as SRSC
from VideoProcessor.SRContext import SRContext
from Player.Context.VideoContext import VideoContext
from .Ui.Ui_OfflineSuperResolutionWindow import Ui_OfflineSuperResolutionWindow

LOGGER=logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class OfflineSuperResolutionWindow(QWidget,Ui_OfflineSuperResolutionWindow):
    def __init__(self,parent=None,srContext:SRContext=None):
        super(OfflineSuperResolutionWindow,self).__init__(parent=parent)
        self.setupUi(self)
        self.srContext:SRContext = srContext
        self.SelectFileButton.clicked.connect(self.selectLoadPath)
        self.SaveDirButton.clicked.connect(self.selectSavePath)
        self.ModelComboBox.activated[str].connect(self.selectInferencer)
        self.RunButton.clicked.connect(self.run)
        self.StopButton.clicked.connect(self.stop)
        self.loadPath = None
        self.savePath = None
        self.inferencerInfo = None
        self.inferencerName = None
        self.last_inferencerName = None
        self.multiplier = 1
        self.encodeWorker = None
        self.encodeThread = None
        # self.inferencerIsLoaded = False

        self.loadInferencerInfo()

    def loadInferener(self):
        self.log("Loading inferencer...")
        if self.last_inferencerName == self.inferencerName:
            self.log("Current inferencer is loaded")
            return True
        multiplier=self.inferencerInfo["Inferencer"][self.inferencerName]["Multiplier"]
        assert multiplier != 0
        self.multiplier = multiplier
        self.srContext.cmdPipe.send(HandlerCmd(HandlerCmd.LoadInferencer,self.inferencerName))
        event_loop = QEventLoop(self)
        while True:
            event_loop.processEvents()
            # print("asdf")
            if self.srContext.msgPipe.poll():
                statusCode:int=self.srContext.msgPipe.recv()
                if statusCode == SRSC.InferredLoaded:
                    self.log("Current inferencer is loaded")
                    self.last_inferencerName = self.inferencerName
                    self.switchInferencerState(True)
                    return True
                elif statusCode == SRSC.LoadInferencerFailed:
                    self.log(f"Current inferencer load failed, status code: {statusCode}")
                    return False
                elif statusCode == SRSC.LoadInferencerInfoFailed:
                    self.log(f"Current inferencer load failed, status code: {statusCode}")
                    return False
                else:
                    self.log(f"Current inferencer load failed, status code: {statusCode}")
                    return False
                
    def switchInferencerState(self,state:bool):
        if state:
            self.LoadingState.setText("就绪")
        else:
            self.LoadingState.setText("未就绪")

    def enableSwitcher(self,state:bool):
        self.RunButton.setEnabled(state)
        # self.StopButton.enabled = state
        self.SelectFileButton.setEnabled(state)
        self.SaveDirButton.setEnabled(state)
        self.LoadPathBox.setReadOnly(not state)
        self.SavePathBox.setReadOnly(not state)


    def run(self):
        self.loadPath = self.LoadPathBox.text()
        self.savePath = self.SavePathBox.text()
        if self.loadPath==""or self.loadPath==None:
            self.log("Load path is empty!")
            return
        if self.savePath=="" or self.savePath==None:
            self.log("Save path is empty!")
            return
        if self.loadPath == self.savePath:
            self.log("Cannot use the same path")
            return
        
        self.log("Started running...")
        self.enableSwitcher(False)
        state = self.loadInferener()
        if not state:
            self.enableSwitcher(True)
            return
        try:
            videoContext = VideoContext(
                                    url=self.loadPath,
                                    source="file"
                                    )
        except Exception:
            self.log("Failed to load video Info")
            self.enableSwitcher(True)
            return

        self.encodeThread = QThread()
        self.encodeWorker = VideoEncodeWorker(videoContext,self.savePath,True,self.srContext,self.multiplier)
        self.encodeWorker.moveToThread(self.encodeThread)
        self.encodeWorker.update_progress_signal.connect(self.progressBar.setValue)
        self.encodeWorker.send_log_signal.connect(self.log)
        self.encodeThread.started.connect(self.encodeWorker.work)
        # self.encodeThread.finished.connect(self.finish)
        self.encodeWorker.process_end_signal.connect(self.finish)
        self.encodeThread.start()
        # self.log("Done!")

    def finish(self):
        self.quitEncoderWorker()
        self.quitEncoderThread()
        self.enableSwitcher(True)

    def stop(self):
        self.log("Stopping...")
        self.quitEncoderWorker()
        self.quitEncoderThread()
        self.enableSwitcher(True)
        self.log("Stopped!")

    def quitEncoderWorker(self):
        if self.encodeWorker is not None:
            self.encodeWorker.quit()
            del self.encodeWorker
            self.encodeWorker = None

    def quitEncoderThread(self):
        if self.encodeThread is not None:
            self.encodeThread.quit()
            self.encodeThread.wait()
            del self.encodeThread
            self.encodeThread = None




    def selectLoadPath(self):
        self.loadPath,_ = QFileDialog.getOpenFileName(None,  "选取文件","./", "All Files (*);") 
        self.LoadPathBox.setText(self.loadPath)
        self.log(f"Load from: {self.loadPath}")

    def selectSavePath(self):
        self.savePath,_ = QFileDialog.getSaveFileName(None,  "文件保存","./", "All Files (*);") 
        self.SavePathBox.setText(self.savePath)
        self.log(f"Save to: {self.savePath}")

    def loadInferencerInfo(self):
        # print("Load Inferencer Info")
        try:
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)),"SuperResolutionInferencer","SuperResolutionInferencerRegister.json"),"r") as f:
            # with open(os.path.join(os.path.dirname(__file__),"SuperResolutionInferencer","SuperResolutionInferencerRegister.json"),"r") as f:
                self.inferencerInfo = json.loads(f.read())

            for key in self.inferencerInfo["Inferencer"].keys():
                self.ModelComboBox.addItem(key)

            index=self.ModelComboBox.findText(self.inferencerInfo["Default"])
            if index==-1:
                index = 0
            self.ModelComboBox.setCurrentIndex(index)
            self.inferencerName = self.inferencerInfo["Default"]
            multiplier=self.inferencerInfo["Inferencer"][self.inferencerName]["Multiplier"]
            assert multiplier != 0
            self.multiplier = multiplier

            self.log("Inferencer Info loaded")
            LOGGER.debug("Inferencer Info loaded")
        except IOError:
            # print("Error reading SuperResolutionInferencerRegister.json")
            LOGGER.error("Error reading SuperResolutionInferencerRegister.json")
            raise RuntimeError("Load InferencerInfo Failed")
            # LOGGER.error(os.path.join(os.path.dirname(__file__),"SuperResolutionInferencer","SuperResolutionInferencerRegister.json"))
            
    def selectInferencer(self,item:str):
        self.inferencerName = item
        if item != self.last_inferencerName:
            self.switchInferencerState(False)
        else:
            self.switchInferencerState(True)
        # print(self.inferencerName)

    def log(self, message:str):
        self.LogBox.moveCursor(self.LogBox.textCursor().End)
        self.LogBox.append(message)


    def closeEvent(self, e:QCloseEvent) -> None:
        self.srContext.cmdPipe.send(HandlerCmd(HandlerCmd.Quit))
        return super().closeEvent(e)