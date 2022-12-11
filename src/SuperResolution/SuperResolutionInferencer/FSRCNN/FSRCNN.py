
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
        self.device = torch.device('cuda')

        self.fsrcnn= FSRCNNModel(4,3)
        # print(os.path.dirname(__file__))
        
        weight = torch.load(os.path.join(os.path.dirname(__file__),"Model","latest.pth"))
        # weight = torch.load("C:\\Users\\White\\Project\\rtsr_client_pyqt\\src\\SuperResolution\\SuperResolutionInferencer\\FSRCNN\\Model\\fsrcnn.pth")
        self.fsrcnn.load_state_dict(weight)
        self.fsrcnn.eval()
        self.fsrcnn.to(self.device)
        print("FSRCNN initializ")

    def process(self, frame):
        
        # print("FSRCNN process image ...")
        start_time = time.perf_counter()
        frame = frame.astype("uint8")[:, :, [2, 1, 0]]
        # print(frame.shape)
        frame = frame.transpose((2,0,1))/255.0
        frame=torch.from_numpy(frame.astype('float32')).to(self.device).unsqueeze(0)
        
        output = self.fsrcnn(frame)
        output = torch.round(output.detach().squeeze()[ [2, 1, 0],:, :].clamp(0, 1) *255).cpu().numpy().transpose((1,2,0)).astype("uint8")
        # print(f"frame time: {(time.perf_counter()-start_time)*1000} ms")
        # print(output.shape)
        # cv2.imwrite("output.png",np.round(output).astype("uint8"))
        
        return output
        # sleep(1)