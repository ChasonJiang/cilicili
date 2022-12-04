
import logging
from multiprocessing import Pipe, Process
from time import sleep
from SuperResolution.HandlerCmd import HandlerCmd
from SuperResolution.SuperResolutionHandler import SuperResolutionHandler

def send(outCmdPipe):
    for i in range(0, 10**100000):
        
        outCmdPipe.send(i)
        print(f"send {i}")
        sleep(0.2)

def recv(inCmdPipe):
    print("asdfkjh")
    while True:
        item=inCmdPipe.recv()
        # if not item:
        #     break
        print(f"recv {item}")
        sleep(2)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO) # DEBUG

    # inCmdPipe,outCmdPipe = Pipe(True)
    # inMsgPipe,outMsgPipe = Pipe(True)
    # inDataPipe1,outDataPipe1 = Pipe(True)
    # inDataPipe2,outDataPipe2 = Pipe(True)
    # # proc = Process(target=send,args=[outCmdPipe])
    # rtsr = SuperResolutionHandler(inCmdPipe, outMsgPipe, inDataPipe1, outDataPipe2)
    # rtsr.start()
    # # proc.start()
    # # print("sadkfjh")
    # # inCmdPipe.send("sdfkgjhsdfglkujh")
    # outCmdPipe.send(HandlerCmd(HandlerCmd.Start,args="FSRCNN"))
    # # inCmdPipe.send(HandlerCmd(HandlerCmd.Start,args="FSRCNN"))
    # # inCmdPipe.send(HandlerCmd(HandlerCmd.Start,args="FSRCNN"))
    # # inCmdPipe.send(HandlerCmd(HandlerCmd.Start,args="FSRCNN"))
    # # inCmdPipe.send(HandlerCmd(HandlerCmd.Start,args="FSRCNN"))
    # # inCmdPipe.send(HandlerCmd(HandlerCmd.Start,args="FSRCNN"))
    # # inCmdPipe.send(HandlerCmd(HandlerCmd.Start,args="FSRCNN"))
    # # inCmdPipe.send(HandlerCmd(HandlerCmd.Start,args="FSRCNN"))
    # rtsr.join()
    pipe1,pipe2 = Pipe()
    p1 = Process(target=send,args=[pipe1])
    p2 = Process(target=recv,args=[pipe2])
    p1.start()
    p2.start()
    # p1.join()
    p2.join()
