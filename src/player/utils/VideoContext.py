import logging
from time import mktime, strptime
import traceback
import ffmpeg

from .HHMMSS2ms import HHMMSS2ms

LOGGER=logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class VideoContext():
    def __init__(self, url, source, req_method=None, req_header=None, req_params=None, req_data=None):
        LOGGER.debug("init VideoContext")
        assert isinstance(url, str)
        assert source.lower() == 'file' or source.lower() == 'network'
        assert isinstance(req_header,dict) or req_header is None
        assert isinstance(req_data,dict) or req_data is None
        if req_method is not None:
            assert req_method.lower() == 'get' or req_method.lower() == 'post'

        self.url = url # str
        self.source = source # str
        self.req_method = req_method # str
        self.req_header = req_header # dict
        self.req_params = req_params # dict
        self.req_data = req_data # dict
        self.frame_width = None # int
        self.frame_height = None # int
        self.frame_channels = 3
        self.duration = None # ms, float
        self.format_duration = None # ms, float
        self.frame_rate = None # float
        self.start_time = None # ms, float
        try:
            self.setVideoInfo()
        except Exception as e:
            raise e

        

    def setVideoInfo(self,):
        try:
            if self.source=='file':
                probe = ffmpeg.probe(self.url)
            elif self.source=="network":
                if self.req_header is None:
                    LOGGER.error("网络流必须提供header！")
                    raise ValueError("网络流必须提供header！")
                header={}
                for k in self.req_header.keys():
                    header[k.lower()] = self.req_header[k]
                self.req_header = header    
                if "user-agent" and "referer" in self.req_header.keys():
                    probe = ffmpeg.probe(self.url,
                                        user_agent=self.req_header["user-agent"], 
                                        referer=self.req_header["referer"], 
                                        headers=self.req_header
                                        )
                elif "user-agent"  in self.req_header.keys():
                    probe = ffmpeg.probe(self.url,
                                        user_agent=self.req_header["user-agent"], 
                                        headers=self.req_header
                                        )
                elif "referer" in self.req_header.keys():
                    probe = ffmpeg.probe(self.url, 
                                        referer=self.req_header["referer"], 
                                        headers=self.req_header
                                        )
                else:
                    probe = ffmpeg.probe(self.url, 
                                        headers=self.req_header
                                        )
        except ffmpeg.Error:
            LOGGER.error("Get video context failed")
            raise IOError("Get video context failed")

        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        # print(video_stream)
        self.frame_width = int(video_stream['width'])
        self.frame_height = int(video_stream['height'])
        avg_frame_rate = str(video_stream['avg_frame_rate'])
        self.start_time = float(video_stream['start_time'])*1000
        self.frame_rate = float(float(avg_frame_rate.split('/')[0])/float(avg_frame_rate.split('/')[1]))
        if "duration" in video_stream.keys():
            self.duration = float(video_stream['duration'])*1000
        elif "DURATION" in video_stream["tags"].keys():
            try:
                self.duration = HHMMSS2ms(video_stream["tags"]['DURATION'])
            except:
                LOGGER.error("DURATION conversion failed")
                raise ValueError("DURATION conversion failed")
        elif "duration"in video_stream["tags"].keys():
            self.duration = float(video_stream["tags"]['duration'])*1000
        self.format_duration = float(probe["format"]['duration'])*1000

        


