
# from multiprocessing import Process
# from multiprocessing import Pipe
import asyncio
import functools
import qasync
from torch.multiprocessing import Process
from torch.multiprocessing import Pipe
import sys
import logging
import torch
from time import sleep
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from CiliCili.MainWindow import MainWindow
from SuperResolution.SRContext import SRContext
from SuperResolution.SuperResolutionHandler import SuperResolutionHandler
from player.PlayerWindow import PlayerWindow
from player.utils.MediaInfo import MediaInfo
from player.CiliCiliPlayer import CiliCiliPlayer
logging.basicConfig(format='--> %(levelname)s : %(message)s', level=logging.ERROR) # DEBUG

# def RTSR(srh_srContext):

#     srh=SuperResolutionHandler(srh_srContext)
#     srh.start()
#     sys.exit(sr.exec_())


# vurl = "http://v16m-default.akamaized.net/1b0a5e06c655f4e6bbb6ee1795b40853/638f69fc/video/tos/alisg/tos-alisg-v-0000/ogQeorDzb1IfAQnGaeTIbdjF4TTGODzAgktoCv/?a=2011&ch=0&cr=0&dr=0&net=5&cd=0%7C0%7C0%7C0&br=4534&bt=2267&cs=0&ds=4&ft=XE5bCqT0mmjPD12e4oyq3wU7C1JcMeF~OD&mime_type=video_mp4&qs=0&rc=NDY6ZDc6ZTtmN2g6OTk1NEBpM2hrajw6Zm1nZzMzODYzNEAvYGAuMmA1X2ExLy4yYl82YSNyMWhqcjRnNnNgLS1kMC1zcw%3D%3D&l=2022120609495901019204616019076160&btag=80000"


def Application(args:list):
    


    logging.basicConfig(format='--> %(levelname)s : %(message)s', level=logging.DEBUG, force=True) # DEBUG
    # media_info = MediaInfo([vurl],[vurl],"network")
    # media_info=MediaInfo(["assets\\5s.mkv", "assets\\5s.mkv"],["assets\\5s.mkv", "assets\\5s.mkv"],"file")
    # media_info = MediaInfo([r"C:\Users\White\Project\rtsr_client_pyqt\assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv"],[r"C:\Users\White\Project\rtsr_client_pyqt\assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv"],"file")
    media_info = MediaInfo(["assets\\360p_all.mkv","assets\\360p_all.mkv"],["assets\\360p_all.mkv","assets\\360p_all.mkv"],"file")
    srContext = args
    app = QApplication(sys.argv)
    # player = BasePlayer()
    player = CiliCiliPlayer(srContext=srContext)
    player.show()
    player.play(media_info)
    # player.play(media_info)
    # sleep(10)
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
    # rtsr=Process(target=RTSR,args=[srh_srContext])
    app.start()
    rtsr.start()
    rtsr.join()
    app.join()




if __name__ == '__main__':

    torch.multiprocessing.set_start_method('spawn', force=True)

    start()