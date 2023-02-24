import logging
from time import mktime, strptime
import ffmpeg

from ..Utils.HHMMSS2ms import HHMMSS2ms

LOGGER=logging.getLogger()

class AudioContext():
    def __init__(self, url, source, req_method=None, req_header=None, req_params=None, req_data=None):
        assert isinstance(url, str)
        assert source.lower() == 'file' or source.lower() == 'network'
        assert isinstance(req_header,dict) or req_header is None
        assert isinstance(req_data,dict) or req_data is None
        if req_method is not None:
            assert req_method.lower() == 'get' or req_method.lower() == 'post'
        LOGGER.debug("init AudioContext")
        self.url = url
        self.source = source
        self.req_method = req_method
        self.req_header = req_header
        self.req_params = req_params
        self.req_data = req_data
        self.sample_rate = None
        self.channels = None
        # self.bit_rate = None
        self.frame_rate = None
        self.duration = None
        self.format_duration  = None
        self.start_time = None
        self.codec_name = None
        self.setAudioInfo()

    def setAudioInfo(self,):
        try:
            if self.source=='file':
                probe = ffmpeg.probe(self.url)
            elif self.source=="network":
                if self.req_header is None:
                    LOGGER.error("网络流必须提供header！")
                    raise ValueError("网络流必须提供header！")
                header = {}
                for k in self.req_header.keys():
                    header[k.lower()] = self.req_header[k]
                self.req_header = header
                if "user-agent" and "referer" in self.req_header.keys():
                    probe = ffmpeg.probe(self.url,user_agent=self.req_header["user-agent"], referer=self.req_header["referer"], headers=self.req_header)
                elif "user-agent"  in self.req_header.keys():
                    probe = ffmpeg.probe(self.url,user_agent=self.req_header["user-agent"], headers=self.req_header)
                elif "referer" in self.req_header.keys():
                    probe = ffmpeg.probe(self.url, referer=self.req_header["referer"], headers=self.req_header)
                else:
                    probe = ffmpeg.probe(self.url, headers=self.req_header)
        except ffmpeg.Error:
            LOGGER.error("Get video context failed")
            raise IOError("Get video context failed")

        stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
        self.sample_rate = int(stream['sample_rate'])
        # self.bit_rate = int(stream['bit_rate'])
        self.channels = int(stream['channels'])
        self.codec_name = str(stream['codec_name'])
        self.start_time = float(stream['start_time'])
        if "duration" in stream.keys():
            self.duration = float(stream['duration'])*1000
        elif "DURATION" in stream["tags"].keys():
            try:
                self.duration = HHMMSS2ms(stream["tags"]['DURATION'])
            except:
                LOGGER.error("DURATION conversion failed")
                raise ValueError("DURATION conversion failed")
        elif "duration"in stream["tags"].keys():
            self.duration = float(stream["tags"]['duration'])*1000
        self.format_duration = float(probe["format"]['duration'])*1000