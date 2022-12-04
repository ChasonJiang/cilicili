


class MediaInfo(object):
    def __init__(self, video_url, audio_url, source, req_method=None, req_header=None, req_params=None, req_data=None):
        assert isinstance(video_url, list) 
        assert isinstance(audio_url, list) 
        assert source.lower() == 'file' or source.lower() == 'network'
        assert isinstance(req_header,dict) or req_header is None
        assert isinstance(req_data,dict) or req_data is None
        if req_method is not None:
            assert req_method.lower() == 'get' or req_method.lower() == 'post'

        self.video_url = video_url
        self.audio_url = audio_url
        self.source = source
        self.req_method = req_method
        self.req_header = req_header
        self.req_params = req_params
        self.req_data = req_data
