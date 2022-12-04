from functools import partial
from threading import Thread
from time import sleep
import ffmpeg
import numpy as np
import cv2

# from src.player.utils.MediaSource import MediaSource

def chunked_file_reader(fp, block_size=1024):
    """生成器函数：分块读取文件内容，使用 iter 函数
    """
    while True:
        chunk = fp.read(block_size)
        # 当文件没有更多内容时，read 调用将会返回空字符串 ''
        if not chunk:
            break
        yield chunk

def process_out(proc):
    headers={"Referer":"https://www.bilibili.com",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56"}
    url="https://xy49x86x255x20xy.mcdn.bilivideo.cn:4483/upgcxcode/65/46/244954665/244954665_f9-1-30032.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1669304864&gen=playurlv2&os=mcdn&oi=3729535386&trid=0000d83c40e821224d94b3e5938a31e4f472u&mid=0&platform=pc&upsig=39d114a2c7e40dc7badcf1e2a87d67e3&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&mcdnid=2002405&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&agrr=0&bw=98889&logo=A0000002"
    # networkMediaSource = MediaSource(url, "network",method="GET",headers=headers)
    # localMediaSource = MediaSource("assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv","local")

    # counter=0
    # pipe=[]
    # for byte in localMediaSource.read():
    #     # pipe.append(networkMediaSource)
    #     if not byte:
    #         break
    #     counter+=1
    #     if counter>2 and counter<5:
    #         continue
    #     proc.stdin.write(byte)
    #     print("in chunk: {} ".format(counter))

    # for byte in pipe:
        
    #     counter+=1
    #     proc.stdin.write(byte)
    #     print("in chunk: {} ".format(counter))

  
def process_in(proc):
    counter=0
    while True:
        counter+=1

        sleep(1)
        # continue
        in_bytes = proc.stdout.read(1920 * 1080 * 3)
        print("in chunk: {} ".format(counter))
        if not in_bytes:
            break
        in_frame = (
            np
            .frombuffer(in_bytes, np.uint8)
            .reshape([1080, 1920, 3])
        )
        # print(in_frame)
        cv2.imwrite("./test/{}.png".format(counter),in_frame)
        # cv2.imshow("Image", in_frame)
        # cv2.waitKey (0)
        # sleep(0.03)
 


def in_frame(proc):
    counter=0
    f = open("out.pcm","wb")
    while True:
        counter+=1

        # sleep(1)
        # continue
        # in_bytes = proc.stdout.read(1920 * 1080 * 3)
        in_bytes = proc.stdout.read(1024*1024*1024)
        
        print("in chunk: {} ".format(counter))
        if not in_bytes:
            break
        f.write(in_bytes)
        # in_frame = (
        #     np
        #     .frombuffer(in_bytes, np.uint8)
        #     .reshape([1080, 1920, 3])
        # )
        # # print(in_frame)
        # cv2.imwrite("./test/{}.png".format(counter),in_frame)
    f.close()


def read_error(proc):
    byte = proc.stderr.read()
    print(byte)


def main():
    # process = (
    #     ffmpeg
    #     .input('assets\[Kamigami&Mabors] Saenai Heroine no Sodatekata Flat - 00 [1080p x265 Ma10p AAC].mkv',thread_queue_size="8")
    #     .output("-" , format='rawvideo', pix_fmt='rgb24')
    #     .run_async(pipe_stdout=True)
    # )
    aurl = "https://xy49x86x255x20xy.mcdn.bilivideo.cn:4483/upgcxcode/65/46/244954665/244954665_f9-1-30280.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1670002720&gen=playurlv2&os=mcdn&oi=3729535384&trid=00009e883647ab544aa6a0589ef8b3bdc6d8u&mid=0&platform=pc&upsig=06ae6e70412c343a1cc6657e3b82ed2b&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&mcdnid=2002405&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&agrr=1&bw=41220&logo=A0000002"

    url="https://xy49x86x255x20xy.mcdn.bilivideo.cn:4483/upgcxcode/65/46/244954665/244954665_f9-1-30280.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&uipk=5&nbs=1&deadline=1669613811&gen=playurlv2&os=mcdn&oi=3729535373&trid=0000641b8773de7f4d83a65686e501b89d90u&mid=0&platform=pc&upsig=34299042ef798649d44199348fe7286f&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&mcdnid=2002405&bvc=vod&nettype=0&orderid=0,3&buvid=&build=0&agrr=1&bw=41220&logo=A0000002"
    headers={
    # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56",
        "Referer":"https://www.bilibili.com",
        "Connection":"keep-alive",
        "Accept":"*/*",
        "Accept-Encoding":"gzip, deflate, br",

        }
    referer = "https://www.bilibili.com"
    user_agent = "\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.56\""
    
    process=(
        ffmpeg
        .input(
                aurl, 
                rw_timeout =5_000_000,
                user_agent=user_agent, 
                referer=referer, 
                headers=headers, 
                method="GET", 
                thread_queue_size=8,
                loglevel="error"
                )
        .output("-" , format='s16le',ac="2", ar="48000")
        .run_async(pipe_stdout=True,pipe_stderr=True)
    )
    
    p1=Thread(target=read_error,args=[process])
    p2 = Thread(target=in_frame,args=[process])
    p1.start()
    p2.start()
    p1.join()
    p2.join()


if __name__ == '__main__':
    main()