

import logging
from player.BasePlayer import BasePlayer
from player.CiliCiliPlayer import CiliCiliPlayer
from player.utils.MediaInfo import MediaInfo
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
headers={
# "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56",
    "Referer":"https://www.bilibili.com",
    "Connection":"keep-alive",
    "Accept":"*/*",
    "Accept-Encoding":"gzip, deflate, br",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56"
    }
referer = "https://www.bilibili.com"
user_agent = "\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56\""
vurl = "https://xy49x86x255x20xy.mcdn.bilivideo.cn:4483/upgcxcode/65/46/244954665/244954665_f9-1-30032.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1670010699&gen=playurlv2&os=mcdn&oi=3729535384&trid=00008c6861b8fd47481b97bb04d58f5cf0fdu&mid=0&platform=pc&upsig=a4c468a185203636a8bbc1a6e7540252&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&mcdnid=2002405&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&agrr=1&bw=98889&logo=A0000002"
aurl = "https://xy49x86x255x20xy.mcdn.bilivideo.cn:4483/upgcxcode/65/46/244954665/244954665_f9-1-30280.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1670010699&gen=playurlv2&os=mcdn&oi=3729535384&trid=00008c6861b8fd47481b97bb04d58f5cf0fdu&mid=0&platform=pc&upsig=7e5cb1fdf13e726652f4dde5588e60ad&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&mcdnid=2002405&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&agrr=1&bw=41220&logo=A0000002"
media_info = MediaInfo([vurl,vurl],[aurl,aurl],"network","GET",req_header=headers)






if __name__ == "__main__":
    # logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.DEBUG, force=True) # DEBUG
    logging.basicConfig(format='--> %(levelname)s : %(message)s', level=logging.DEBUG, force=True) # DEBUG
    media_info=MediaInfo(["assets\\5s.mkv", "assets\\5s.mkv"],["assets\\5s.mkv", "assets\\5s.mkv"],"file")
    # media_info = MediaInfo([r"C:\Users\White\Project\rtsr_client_pyqt\assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv"],[r"C:\Users\White\Project\rtsr_client_pyqt\assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv"],"file")
   
    app = QApplication(sys.argv)
    # player = BasePlayer()
    player = CiliCiliPlayer()
    player.show()
    player.play(media_info)
    # print("asdfgasdfgsdf")
    # window = Window()
    # window.show()
    sys.exit(app.exec_())
