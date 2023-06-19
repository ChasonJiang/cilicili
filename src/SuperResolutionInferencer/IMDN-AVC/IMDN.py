
import logging
from multiprocessing.connection import PipeConnection
import os
from time import sleep
import time

import cv2
from .Model.architecture import IMDN_E, IMDN_RTC
import torch
from torch import amp
from VideoProcessor.Inferencer import Inferencer
import numpy as np
from PyQt5.QtCore import *
LOGGER=logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class IMDN(Inferencer):
    def __init__(self,):
        # eventLoop = QEventLoop()
        # eventLoop.processEvents()
        self.device = torch.device('cuda:0')

        self.model= IMDN_RTC(upscale=2)
        # self.model= IMDN_RTC(upscale=2)
        
        # print(os.path.dirname(__file__))
        
        weight = torch.load(os.path.join(os.path.dirname(__file__),"Model","avc_2x_latest.pth"))
        # weight = torch.load("C:\\Users\\White\\Project\\rtsr_client_pyqt\\src\\SuperResolution\\SuperResolutionInferencer\\FSRCNN\\Model\\fsrcnn.pth")
        self.model.load_state_dict(weight)
        # self.model.half()
        self.model.to(self.device)
        self.model.eval()
        self.ones = None
        LOGGER.debug("IMDN-AVC initialized")

    def process(self, frame_buffer_queue):
        
        # print("FSRCNN process image ...")
        
        frame = frame_buffer_queue.get()
        start_time = time.perf_counter()
        output = None
        if frame is not None:
            frame = frame.astype("uint8")[:, :, [2, 1, 0]]
            # print(frame.shape)
            # H, W, C -> C, H, W
            frame = frame.transpose((2,0,1))/255.0
            frame=torch.from_numpy(frame.astype('float32')).to(self.device)
            # frame = frame.unsqueeze(0)
            frame_left,frame_right,is_left_and_right=self.frame_split(frame)
            frame_right = frame_right.unsqueeze(0)
            # frame_left_scaled = (imresize(frame_left,2,True).clamp(0, 1) *255).int()
            frame_left=frame_left.unsqueeze(0)
            frame_left=torch.nn.functional.interpolate(frame_left,scale_factor=1/2.0,mode='bicubic')
            frame_left_scaled=(torch.nn.functional.interpolate(frame_left,scale_factor=4,mode='bicubic').squeeze(0).clamp(0, 1) *255).int()

            
            # with amp.autocast(self.device.type):
            output = self.model(frame_right)
            output = torch.round(output.detach().squeeze().clamp(0, 1) *255).int()
            
            output = torch.cat([frame_left_scaled,output],dim=2 if is_left_and_right else 1).int()
            # RGB -> BGR and C, H, W -> H, W, C
            output = output[ [2, 1, 0],:, :].permute(1,2,0)
            
            if self.ones is None :
                self.ones = torch.ones((output.shape[0],output.shape[1],1), dtype=torch.uint8).cuda()
            elif (self.ones.shape[0] != output.shape[0]) or (self.ones.shape[1] != output.shape[1]) or (self.ones.shape[2] != output.shape[2]):
                self.ones = torch.ones((output.shape[0],output.shape[1],1), dtype=torch.uint8).cuda()
                
            output = torch.cat([output,self.ones ], dim=2)
            output =  [output]
            LOGGER.debug(f"frame time: {(time.perf_counter()-start_time)*1000:.3f} ms")


        # output = [torch.ones((frame.shape[0]*4, frame.shape[1]*4,4),dtype=torch.uint8).cuda()]
        # torch.cuda.synchronize()
        # print(output.shape)
        # cv2.imwrite("output.png",np.round(output).astype("uint8"))
        
        return output
        # sleep(1)

    def frame_split(self,frame:torch.Tensor):
        is_left_and_right = False
        if frame.shape[1]>frame.shape[2]:
            frame_left = frame[:,:frame.shape[1]//2,:].clone()
            frame_right = frame[:,frame.shape[1]//2:,:].clone()
        else:
            is_left_and_right=True
            frame_left = frame[:,:,:frame.shape[2]//2].clone()
            frame_right = frame[:,:,frame.shape[2]//2:].clone()

        return frame_left,frame_right,is_left_and_right