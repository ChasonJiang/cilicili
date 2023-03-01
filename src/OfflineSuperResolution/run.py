import os
import sys
from torch.multiprocessing import Process
from torch.multiprocessing import Pipe
import sys
import logging
import torch
from time import sleep
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from VideoProcessor.SRContext import SRContext
from VideoProcessor.VideoProcessorHandler import VideoProcessorHandler
from OfflineSuperResolution.OfflineSuperResolutionWindow import OfflineSuperResolutionWindow

# logging.basicConfig(format='--> %(levelname)s : %(message)s', level=logging.ERROR) # DEBUG

def setEnv(path:str):
    os.environ["Path"] = os.environ["Path"] + ";"+path


def runOfflineSuperResolution(srContext:SRContext):
    app = QApplication([])
    window = OfflineSuperResolutionWindow(srContext=srContext)
    window.show()
    sys.exit(app.exec_())


def run():
    setEnv("./bin")
    torch.multiprocessing.set_start_method('spawn', force=True)
    inCmdPipe,outCmdPipe = Pipe(True)
    inMsgPipe,outMsgPipe = Pipe(True)
    vph_outDataPipe,app_inDataPipe = Pipe(True)
    vph_inDataPipe,app_outDataPipe = Pipe(True)
    app_srContext = SRContext(outCmdPipe,inMsgPipe,app_inDataPipe, app_outDataPipe)
    vph_srContext = SRContext(inCmdPipe, outMsgPipe,vph_inDataPipe ,vph_outDataPipe)

    osrWindow=Process(target=runOfflineSuperResolution,args=[app_srContext])
    vph = VideoProcessorHandler(vph_srContext)
    vph.start()
    osrWindow.start()
    # vph.join()
    # osrWindow.join()

if __name__ == "__main__":
    run()
