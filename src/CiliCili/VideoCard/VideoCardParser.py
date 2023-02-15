

import time
from .VideoCard import VideoCard


class VideoCardParser():
    """
        VideoCardParser
        parse dict from a request for a video card

        data is a dictionary,like this:
        {
            "from":"homepage" or "search",
            "data":{
                "item":[
                    {
                        'id':,
                        'bvid':,
                        'cid':,
                        'goto':,
                        'uri':,
                        'pic':,
                        'title':,
                        'duration':,
                        'pubdate':,
                        'owner':, 
                        'stat':, 
                        'av_feature':, 
                        'is_followed':, 
                        'rcmd_reason':, 
                        'show_info':, 
                        'track_id':, 
                        'pos':, 
                        'room_info':, 
                        'ogv_info':, 
                        'business_info':, 
                        'is_stock':,
                    }
                    ...
                ],
                ...
            } 
            or 
            [
                {
                    "result_type":,
                    "data":[
                        {
                            "type": 
                        }
                    ]
                },
                ...
            ]

        }

    
    """
    def __init__(self,data:dict=None,parent=None):
        self.data:dict = data
        self.parent = parent
        
    def parse(self,data=None,parent=None):
        self.data = data if data is not None else self.data
        self.parent = parent if parent is not None else self.parent
        assert self.data is not None
        assert self.parent is not None
        _videoCardList = None
        if data["from"] == "homepage":
            items = self.data["data"]["item"]
            _videoCardList = [self.videoParser(items[i],parent) for i in range(len(items))]
        elif data["from"] == "search":
            results = self.data["data"]
            page = data["page"]
            _videoCardList = []
            episodeList = []
            videoList = []
            for result in results:
                if result["result_type"] in ["media_bangumi","media_ft"] and len(result["data"])!=0 and page==1:
                    for item in result["data"]:
                        episodeList.append(self.episodeParser(item,parent))
                elif result["result_type"] == "video":
                    for item in result["data"]:
                        videoList.append(self.videoParser(item,parent))
            _videoCardList = episodeList + videoList
        # print(data)
        
        return _videoCardList

    def episodeParser(self,item:dict,parent)->VideoCard:

        videoCard = VideoCard(parent)
        data = item
        data_keys = data.keys()
        d={
            "title":data["title"],
            "media_id":data["media_id"]if "media_id" in data_keys else None,
            "season_id":data["season_id"]if "season_id" in data_keys else None,
            "description":data["desc"],
        }
        videoCard.data=d
        videoCard.pic = data["cover"]
        videoCard.title = data["title"]
        timeArray = time.localtime(float(abs(data["pubtime"])))
        otherStyleTime = time.strftime("%Y-%m-%d-%H:%M", timeArray)
        videoCard.authorInfo = data["season_type_name"] +" "+otherStyleTime
        videoCard.dateInfo = "评分: "+str(data["media_score"]["score"]) + " " + str(data["index_show"])
        videoCard.type = "episode"
        return videoCard


    def videoParser(self,item:dict,parent)->VideoCard:
        # print(parent)
        videoCard = VideoCard(parent)
        item_keys = item.keys()
        data={
            "aid":None,
            "bvid":None,
        }
        if "aid" in item_keys:
            data["aid"] = item["aid"]
        if "bvid" in item_keys:
            data["bvid"] = item["bvid"]
        if "cid" in item_keys:
            data["cid"] = item["cid"]
        if "owner" in item_keys:
            data["owner"] = item["owner"]
        else:
            data["owner"] = {
                "mid":item["mid"],
                "name":item["author"],
                "face":item["upic"],
            }
        data["title"] = item["title"]
        videoCard.data = data
        timeArray = time.localtime(abs(float(item["pubdate"])))
        otherStyleTime = time.strftime("%Y-%m-%d-%H:%M", timeArray)
        videoCard.authorInfo = data["owner"]["name"] +"  "+otherStyleTime
        if "stat" in item_keys:
            videoCard.dateInfo = "播放: "+str(item["stat"]["view"])+" "+"点赞: "+str(item["stat"]["like"])
        else:
            videoCard.dateInfo = "播放: "+str(item["play"])+" "+"收藏: "+str(item["favorites"])
        pic:str = item["pic"]
        if pic.find("https://") == -1 and pic.find("http://") == -1:
            pic = "https:"+pic
        videoCard.pic = pic
        videoCard.title = item["title"]
        videoCard.type = "video"
        
        
        return videoCard
            

        

