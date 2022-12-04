import requests as R

def chunked_file_reader(fp, chunk_size=1024):
    """生成器函数：分块读取文件内容，使用 iter 函数
    """
    while True:
        chunk = fp.read(chunk_size)
        # 当文件没有更多内容时，read 调用将会返回空字符串 ''
        if not chunk:
            break
        yield chunk



class MediaSource():
    def __init__(self, url, source, req_method=None, req_header=None, req_params=None, req_data=None):
        """
            url(str): URL of the media file. http://localhost/media.mp4 or ./media.mp4
            type(str): type of the media file. network or local
        """
        assert isinstance(url, str)
        assert source.lower() == 'file' or source.lower() == 'network'
        assert isinstance(req_header,dict) or req_header is None
        assert isinstance(req_data,dict) or req_data is None
        if req_method is not None:
            assert req_method.lower() == 'get' or req_method.lower() == 'post'

        self.url = url
        self.source = source
        self.req_method = req_method
        self.req_header = req_header
        self.req_params = req_params
        self.req_data = req_data
        self.stream=None

    def create_stream(self, ):
        # self.protocol = None

        if self.source == 'network':
            return self.create_stream_from_network()

        elif self.source == 'file':
            return self.create_stream_from_file()

    def create_stream_from_network(self,):
        def stream_generator(chunk_size=1024*1024):
            if self.req_header is None:
                raise ValueError("Use of network flow must be accompanied by a request header!")
            res =None
            if self.req_method.lower()=='post':
                res = R.post(self.url, data=self.req_data, headers = self.req_header, stream=True)

            elif self.req_method.lower()=='get':
                res = R.get(self.url, params = self.req_params, headers = self.req_header, stream=True)
                print(res.headers)

            if res.status_code != 200:
                raise RuntimeError('Cannot request this source! Status Code: {}'.format(res.status_code))

            for chunk in res.iter_content(chunk_size):
                yield chunk

        return stream_generator


    def create_stream_from_file(self,):
        def stream_generator(chunk_size=1024*1024):
            with open(self.url, 'rb') as f:
                for chunk in chunked_file_reader(f,chunk_size):
                    yield chunk
        return stream_generator



if __name__ == '__main__':
    headers={"Referer":"https://www.bilibili.com",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56"}
    localMediaSource = MediaSource("assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv","file")
    url="https://xy49x86x255x20xy.mcdn.bilivideo.cn:4483/upgcxcode/65/46/244954665/244954665_f9-1-30032.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1669368054&gen=playurlv2&os=mcdn&oi=3729535386&trid=00007a112f26b738449497f3eadb954886fdu&mid=0&platform=pc&upsig=84d32fe58673bbf642f790b36927fdd6&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&mcdnid=2002405&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&agrr=1&bw=98889&logo=A0000002"
    networkMediaSource = MediaSource(url, "network",req_method="get",req_header=headers)
    # res=R.get(url,headers=headers, stream=True)
    counter=0
    pipe=[]
    f = open("./video","wb")
    steam = networkMediaSource.create_stream()
    for chunk in steam(chunk_size=10*1024*1024):
        counter += 1
        print("Chunk: {} \n".format(counter))
        f.write(chunk)
        # pipe.append(chunk)
    f.close()