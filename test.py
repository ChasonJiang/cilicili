import os

import ffmpeg 


def headers_converter(headers:dict):
    headers_ffmpeg_style = ""
    counter = 0
    for k in headers.keys():
        counter += 1
        headers_ffmpeg_style +='\"{:s}: {:s}\"'.format(k,headers[k])
        # if counter==len(headers.keys()):
        #     break
        headers_ffmpeg_style += "$\'\\r\\n\'"
        # print('\"{:s}: {:s}\"'.format(k,headers[k])+r"$'\r\n'")
    return headers_ffmpeg_style


if __name__ == '__main__':
    url="https://xy49x86x255x20xy.mcdn.bilivideo.cn:4483/upgcxcode/65/46/244954665/244954665_f9-1-30032.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1669743923&gen=playurlv2&os=mcdn&oi=3729535384&trid=0000e6f3dfc787de4f9281d3ae81257d7611u&mid=0&platform=pc&upsig=e404beede1c99d5af8f0e2708b1e5a4c&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&mcdnid=2002405&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&agrr=1&bw=98889&logo=A0000002"
    headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56",
        "Referer":"https://www.bilibili.com",
        "Connection":"keep-alive",
        "Accept":"*/*",
        "Accept-Encoding":"gzip, deflate, br",

        }
    referer = "https://www.bilibili.com"
    user_agent = "\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56\""
    # cmd = "ffprobe -i {} -user_agent {}  -headers {} -method GET -show_format -show_streams -print_format json "
    cmd = "ffprobe -i {} -user_agent {}  -referer {} -method GET -show_format -show_streams -print_format json "
    # cmd = "ffmpeg -i {} -user_agent {} -headers {} -method GET -c copy tst.mp4"
    # print(headers_converter(headers))
    # os.system(cmd.format(url,user_agent, headers_converter(headers)))
    # h = headers_converter(headers)
    # os.system(cmd.format(url, user_agent, referer))
    probe = ffmpeg.probe(url,user_agent=user_agent, referer=referer, headers=headers,method="GET")
    # video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
    # width = int(video_stream['width'])
    # height = int(video_stream['height'])
    print(probe)