

from .VideoCard import VideoCard


class VideoCardParser():
    """
        VideoCardParser
        parse dict from a request for a video card

        data is a dictionary,like this:
        {
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
    
    """
    def __init__(self,data:dict=None,parent=None):
        self.data:dict = data
        self.parent = parent
        
    def parse(self,data=None,parent=None):
        self.data = data if data is not None else self.data
        self.parent = parent if parent is not None else self.parent
        assert self.data is not None
        assert self.parent is not None
        items = self.data["item"]
        # print(data)
        _videoCardList = [self.parser(items[i],parent) for i in range(len(items))]

        return _videoCardList


    def parser(self,item:dict,parent)->VideoCard:
        # print(parent)
        videoCard = VideoCard(parent)
        item_keys = item.keys()
        if "aid" in item_keys:
            videoCard.aid = item["aid"]
        else:
            videoCard.bvid = item["bvid"]
        videoCard.cid = item["cid"]
        
        videoCard.uri = item["uri"]
        videoCard.pic = item["pic"]
        videoCard.title = item["title"]
        videoCard.duration = item["duration"]
        videoCard.owner = item["owner"]
        videoCard.stat = item['stat']
        videoCard.pubdate = item['pubdate']
        videoCard.is_followed = item["is_followed"]
        videoCard.rcmd_reason = item["rcmd_reason"]
        
        return videoCard
            

        

