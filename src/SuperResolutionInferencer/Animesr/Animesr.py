
import logging
from multiprocessing.connection import PipeConnection
import os
from time import sleep
import time

import cv2
import torch
from torch import amp

from.animesr.archs.vsr_arch import MSRSWVSR
from .animesr.utils.inference_base import get_inference_model
from VideoProcessor.Inferencer import Inferencer
import numpy as np
from PyQt5.QtCore import *
LOGGER=logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

class Animesr(Inferencer):
    def __init__(self,):
        self.device = torch.device('cuda:0')
        
        self.model = MSRSWVSR(num_feat=64, num_block=[5, 3, 2], netscale=4)
        weight = torch.load(os.path.join(os.path.dirname(__file__),"Models","AnimeSR_v2.pth"))
        self.model.load_state_dict(weight)
        # self.model.half()
        self.model.to(self.device)
        self.model.eval()
        self.ones = None
        self.state = None
        self.out = None
        self.prev = None
        self.cur = None 
        self.next = None
        self.is_first =True
        LOGGER.debug("Animesr-x4 initialized")

    @torch.no_grad()
    def process(self, frame_buffer_queue):
        
        # print("FSRCNN process image ...")
        
        frame:np.ndarray = frame_buffer_queue.get()
        start_time = time.perf_counter()
        output = None
        if frame is None:
            return None
        
        if self.is_first:
            self.is_first = False
            self.cur = torch.zeros((3,frame.shape[0],frame.shape[1]),dtype=torch.float32).to(self.device)
            # self.state = self.cur.new_zeros(1, 64, frame.shape[0], frame.shape[1])
            # self.out = self.cur.new_zeros(1, 3, frame.shape[0] * 4, frame.shape[1] * 4)
            frame = frame_buffer_queue.get()
            if frame is None:
                self.next = torch.zeros((3,frame.shape[0],frame.shape[1]),dtype=torch.float32).to(self.device)
            else:
                self.next = self.transfroms(frame)

        frame = self.transfroms(frame)
        self.prev = self.cur
        self.cur = self.next
        self.next = frame
        # frame = frame.unsqueeze(0)
        prev_left,prev_right,_=self.frame_split(self.prev)
        prev_right = prev_right.unsqueeze(0)
        cur_left,cur_right,is_left_and_right=self.frame_split(self.cur)
        cur_right = cur_right.unsqueeze(0)
        next_left,next_right,_=self.frame_split(self.prev)
        next_right = next_right.unsqueeze(0)
        cur_left_scaled=(torch.nn.functional.interpolate(cur_left.unsqueeze(0),scale_factor=4,mode='bicubic').squeeze(0).clamp(0, 1) *255).int()
        
        if (self.state is None) or (self.out is None):
            self.state = self.cur.new_zeros(1, 64, cur_right.shape[2], cur_right.shape[3])
            self.out = self.cur.new_zeros(1, 3, cur_right.shape[2] * 4, cur_right.shape[3] * 4)
            # self.is_first = False
        # with amp.autocast(self.device.type):
        self.out,self.state = self.model.cell(torch.cat((prev_right, cur_right, next_right), dim=1), self.out, self.state)
        output = torch.round(self.out.detach().squeeze().clamp(0, 1) *255).int()
        
        output = torch.cat([cur_left_scaled,output],dim=2 if is_left_and_right else 1).int()
        # RGB -> BGR and C, H, W -> H, W, C
        output = output[ [2, 1, 0],:, :].permute(1,2,0)
        
        if self.ones is None :
            self.ones = torch.ones((output.shape[0],output.shape[1],1), dtype=torch.uint8).cuda()
        elif (self.ones.shape[0] != output.shape[0]) or (self.ones.shape[1] != output.shape[1]) or (self.ones.shape[2] != output.shape[2]):
            self.ones = torch.ones((output.shape[0],output.shape[1],1), dtype=torch.uint8).cuda()
            
        output = torch.cat([output,self.ones ], dim=2)
        output =  [output]
        LOGGER.debug(f"frame time: {(time.perf_counter()-start_time)*1000:.3f} ms")
        
        return output
        # sleep(1)


    def transfroms(self,frame:np.ndarray)->torch.Tensor:
        frame = frame.astype("uint8")[:, :, [2, 1, 0]]
        # print(frame.shape)
        # H, W, C -> C, H, W
        frame = frame.transpose((2,0,1))/255.0
        frame=torch.from_numpy(frame.astype('float32')).to(self.device)
        return frame

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