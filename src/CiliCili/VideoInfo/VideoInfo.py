from bilibili_api import Credential,video
from qasync import asyncSlot
import aiohttp
import time
from Player.Utils.MediaInfo import MediaInfo

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


class VideoInfo():
    videoAPI:video.Video = None
    info:dict = None
    credential = None

    bvid = None
    aid = None
    defult_cid = 0
    videoFormats:dict = {} 
    # cid = 


    def __init__(self,bvid:str=None,aid:int=None,credential:Credential=None):
        if bvid or aid:
            self.init(bvid,aid,credential)
        # pass

    def init(self,bvid:str=None,aid:int=None,credential:Credential=None):
        self.bvid = bvid
        self.aid = aid
        self.credential = credential
        self.videoAPI = video.Video(bvid=self.bvid, aid=self.aid, credential=credential)

    @asyncSlot()
    async def requestInfo(self,bvid:str=None,aid:int=None,credential:Credential=None):
        self.bvid = bvid if bvid is not None else self.bvid
        self.aid = aid if aid is not None else self.aid
        self.credential = credential if credential is None else self.credential
        # assert self.credential is not None
        assert (self.aid is not None) or ( self.bvid is not None)
        info = await self.videoAPI.get_info()
        cid_list = []
        for item in info["pages"]:
            cid = item["cid"]
            cidDict = {
                "title":item["part"],
                "cid":cid,
            }
            cid_list.append(cidDict)
        self.defult_cid = cid_list[0]["cid"]

        self.loadInfo(info,cid_list)


    def loadInfo(self,info:dict,cid_list:list):
        info_keys = info.keys()
        timeArray = time.localtime(float(abs(info["pubdate"])))
        pubdate = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        num_views = info["stat"]["view"]
        num_like = info["stat"]["like"]
        desc_v2 = info["desc_v2"][0]
        desc = ""
        if desc_v2["type"] == 1:
            desc = desc_v2["raw_text"]
        else:
            desc = desc_v2["raw_text"] + "  @"+str(desc_v2["biz_id"])

        self.info = {
            "type":"video",
            "title":info["title"],
            "id":info["bvid"] if "bvid" in info_keys else info["aid"],
            "description":desc,
            "playInfo":"播放: {} 点赞: {}  {}".format(num_views,num_like,pubdate),
            "cids":cid_list
        }
        """
            cids like this:
            [
                {
                    "title":<title>,
                    "cid":<cid>
                },
                ...
            ]
        """

    def get_defult_cid(self):
        return self.defult_cid

    @asyncSlot()
    async def createMediaInfo(self,cid:int=None,page_index:int=None):
        content= await self.videoAPI.get_download_url(page_index=page_index,cid=cid)
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