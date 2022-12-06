
from multiprocessing import Process
from multiprocessing import Pipe
import sys
import logging
from time import sleep
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from SuperResolution.SRContext import SRContext
from SuperResolution.SuperResolutionHandler import SuperResolutionHandler
from player.utils.MediaInfo import MediaInfo
from player.CiliCiliPlayer import CiliCiliPlayer




# def RTSR():
#     # while True:
#     #     print("run rtsr")
#     #     sleep(0.5)
#     srh = 
#     srh = 



def Application(args:list):
    logging.basicConfig(format='--> %(levelname)s : %(message)s', level=logging.DEBUG, force=True) # DEBUG

    # media_info=MediaInfo(["assets\\5s.mkv", "assets\\5s.mkv"],["assets\\5s.mkv", "assets\\5s.mkv"],"file")
    # media_info = MediaInfo([r"C:\Users\White\Project\rtsr_client_pyqt\assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv"],[r"C:\Users\White\Project\rtsr_client_pyqt\assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv"],"file")
    media_info = MediaInfo(["assets\\360p.mkv"],["assets\\360p.mkv"],"file")
    srContext = args
    app = QApplication(sys.argv)
    # player = BasePlayer()
    player = CiliCiliPlayer(srContext=srContext)
    player.show()
    player.play(media_info)
    # print("asdfgasdfgsdf")
    # window = Window()
    # window.show()
    sys.exit(app.exec_())


def start():
    inCmdPipe,outCmdPipe = Pipe(True)
    inMsgPipe,outMsgPipe = Pipe(True)
    srh_outDataPipe,app_inDataPipe = Pipe(True)
    srh_inDataPipe,app_outDataPipe = Pipe(True)
    app_srContext = SRContext(outCmdPipe,inMsgPipe,app_inDataPipe, app_outDataPipe)
    srh_srContext = SRContext(inCmdPipe, outMsgPipe,srh_inDataPipe ,srh_outDataPipe)

    app=Process(target=Application,args=[app_srContext])
    # rtsr = Process(target=RTSR,)
    rtsr = SuperResolutionHandler(srh_srContext)
    app.start()
    rtsr.start()
    rtsr.join()
    app.join()



if __name__ == '__main__':
    start()