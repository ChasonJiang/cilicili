
from multiprocessing.connection import PipeConnection
import os
from time import sleep
import time

import cv2
from .Model.FSRCNNModel import FSRCNNModel
import torch
from SuperResolution.Inferencer import Inferencer
import numpy as np
from PyQt5.QtCore import *

class FSRCNN(Inferencer):
    def __init__(self,):
        # eventLoop = QEventLoop()
        # eventLoop.processEvents()
        self.device = torch.device('cuda:0')

        self.fsrcnn= FSRCNNModel(4,3)
        
        # print(os.path.dirname(__file__))
        
        weight = torch.load(os.path.join(os.path.dirname(__file__),"Model","latest.pth"))
        # weight = torch.load("C:\\Users\\White\\Project\\rtsr_client_pyqt\\src\\SuperResolution\\SuperResolutionInferencer\\FSRCNN\\Model\\fsrcnn.pth")
        self.fsrcnn.load_state_dict(weight)
        self.fsrcnn.eval()
        self.fsrcnn.to(self.device)
        print("FSRCNN initialized")

    def process(self, frame_buffer_queue):
        
        # print("FSRCNN process image ...")
        
        frame = frame_buffer_queue.get()
        start_time = time.perf_counter()
        output = None
        if frame is not None:
            frame = frame.astype("uint8")[:, :, [2, 1, 0]]
            # print(frame.shape)
            frame = frame.transpose((2,0,1))/255.0
            frame=torch.from_numpy(frame.astype('float32')).to(self.device).unsqueeze(0)
            
            output = self.fsrcnn(frame)
            output = torch.round(output.detach().squeeze()[ [2, 1, 0],:, :].clamp(0, 1) *255).cpu().numpy().transpose((1,2,0)).astype("uint8")
            print(f"frame time: {(time.perf_counter()-start_time)*1000} ms")
            output =  [output]

       
        # print(output.shape)
        # cv2.imwrite("output.png",np.round(output).astype("uint8"))
        
        return output
        # sleep(1)