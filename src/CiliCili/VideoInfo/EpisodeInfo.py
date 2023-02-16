from bilibili_api import Credential,bangumi
from qasync import asyncSlot
import aiohttp
import time
from player.utils.MediaInfo import MediaInfo

HEADERS={
    # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56",
    "Referer":"https://www.bilibili.com",
    "Connection":"keep-alive",
    "Accept":"*/*",
    "Accept-Encoding":"gzip, deflate, br",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56"
}
# REFERER = "https://www.bilibili.com"
# USER_AGENT = "\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56\""


class EpisodeInfo():
    video:bangumi.Bangumi = None
    info:dict = None
    credential = None

    media_id = -1
    ssid = -1
    epid = -1
    episodeObjList:list = None
    episodeObjDict:dict = {}
    defult_epid = -1
    videoFormats:dict = {} 
    # cid = 


    def __init__(self,media_id:int=-1,ssid:int=-1,epid:int=-1,credential:Credential=None):
        if media_id !=-1 or ssid !=-1 or epid !=-1:
            self.init(media_id,ssid,epid,credential)
        # pass

    def init(self,media_id:int=-1,ssid:int=-1,epid:int=-1,credential:Credential=None):
        self.media_id = media_id
        self.ssid = ssid
        self.epid = epid
        self.credential = credential
        self.videoAPI = bangumi.Bangumi(media_id=self.media_id, ssid=self.ssid, epid=self.epid, credential=credential)

    @asyncSlot()
    async def requestInfo(self,media_id:int=-1,ssid:int=-1,epid:int=-1,credential:Credential=None):
        self.media_id = media_id if media_id == -1 else self.media_id
        self.ssid = ssid if ssid == -1 else self.ssid
        self.epid = epid if epid == -1 else self.epid
        self.credential = credential if credential is None else self.credential
        # assert self.credential is not None
        assert (self.media_id != -1) or ( self.ssid != -1)
        info = await self.videoAPI.get_overview()

        self.episodeObjList = await self.videoAPI.get_episodes()
        episodeList=[]
        counter =0
        for episodeObj in self.episodeObjList:
            self.episodeObjDict[episodeObj.get_epid()] = episodeObj
            epid = episodeObj.get_epid()
            # ep_info=await episodeObj.get_episode_info()
            # title = ep_info["h1Title"]
            counter +=1
            title = f"第{counter}话"
            episodeList.append({
                "epid":epid,
                "title":title
            })

        self.defult_epid = self.episodeObjList[0].get_epid()
        self.loadInfo(info,episodeList)

    def get_defult_epid(self):
        return self.defult_epid

    def loadInfo(self,info:dict,episodeList:list):
        pubdate = info["publish"]["pub_time"]
        num_views = info["stat"]["views"]
        num_like = info["stat"]["likes"]
        self.info = {
            "type":"episode",
            "title":info["title"],
            "id":info["media_id"],
            "description":info["evaluate"],
            "playInfo":"播放: {} 点赞: {}  {}".format(num_views,num_like,pubdate),
            "epids":episodeList
        }
        """
            epids like this:
            [
                {
                    "title":<title>,
                    "epid":<cid>
                },
                ...
            ]
        """


    @asyncSlot()
    async def createMediaInfo(self,epid:int):
        episodeObj:bangumi.Episode = self.episodeObjDict[epid]
        content = await episodeObj.get_download_url()
        self.setVideoFormat(content["support_formats"])
        dash = content["dash"]
        return self.packUpMediaInfo(dash)

    def packUpMediaInfo(self,dash:dict):
        """
            Result: dict
                {
                    "defult": <qn_code>,
                    "media_info": {
                        <qn_code>: [<MediaInfo>,...]
                    }
                    
                }
        """
        audio = self.chooseAudio(dash["audio"])
        mediaInfoDict={}
        best_id = 0
        bed_id = 999999999
        for item in dash["video"]:
            id = item["id"]
            if id>best_id:
                best_id = id
            if id<bed_id:
                bed_id = id

            if id not in mediaInfoDict.keys():
                mediaInfoDict[id]=[]
            mi = MediaInfo([item["baseUrl"]],[audio['baseUrl']],"network",'GET',HEADERS)
            mediaInfoDict[id].append(mi)
            for idx,url in enumerate(item["backupUrl"]):
                a_idx = idx%len(audio['backupUrl'])
                mi = MediaInfo([url],[audio['backupUrl'][a_idx]],"network",'GET',HEADERS)
                mediaInfoDict[id].append(mi)

        return {
            'defult':bed_id,
            "media_info":mediaInfoDict
        }

    def chooseAudio(self,items:list):
        items.sort(key=lambda x:x['id'],reverse=True)
        if len(items)>3:
            return items[1]
        else:
            return items[0]


    def setVideoFormat(self, items:list):
        for item in items:
            self.videoFormats[item['quality']] = item['new_description']