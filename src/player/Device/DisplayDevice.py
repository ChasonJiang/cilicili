from contextlib import contextmanager
import sys
from time import perf_counter, sleep
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
# from PySide2.QtGui import *
# from PySide2.QtCore import *
# from PySide2.QtWidgets import *
import OpenGL.GL as gl
# import OpenGL.GLUT as glut
import cv2
import numpy as np
import torch
# torch.cuda.init()
import pycuda.driver
import pycuda.autoinit
# import pycuda.autoprimaryctx
# import pycuda.gl.autoinit
# import pycuda.gl
from pycuda.gl import graphics_map_flags
from glumpy import gloo, app as glumpy_app
glumpy_app.use("qt5")

class DisplayDevice(QOpenGLWidget):
# class DisplayDevice(QtOpenGL.QGLWidget):

    setup_signal = pyqtSignal(list)
    update_signal_np = pyqtSignal(np.ndarray)
    update_signal_tensor = pyqtSignal(torch.Tensor)

    VERTEX_CODE="""
    uniform float scale;
    attribute vec2 position;
    attribute vec2 texcoord;
    varying vec2 v_texcoord;
    void main()
    {
        v_texcoord = texcoord;
        gl_Position = vec4(scale*position, 0.0, 1.0);
    } 
    """
    FRAGMENT_CODE="""
    uniform sampler2D tex;
    varying vec2 v_texcoord;
    void main()
    {
        gl_FragColor = texture2D(tex, v_texcoord);
    } 
    """
    def __init__(self, parent:QWidget=None, tex_size:list=None,is_cuda=False):
        super(DisplayDevice, self).__init__(parent)
        self.setStyleSheet("*{\n"
                            "background-color: rgba(0,0,0,0);\n"
                            "}")
        self.setup_signal.connect(self.setup)
        self.update_signal_np.connect(self.update)
        self.update_signal_tensor.connect(self.update)
        self.tex_size=tex_size
        # self.setAutoBufferSwap(False)
        self.setMouseTracking(True)
        self.painter = QPainter()
        self.program = None
        self.cuda_buffer = None
        self.tex = None
        self.is_cuda=is_cuda
        self.frame = None
        if parent is not None:
            self.resize(parent.width(), parent.height())
        if self.is_cuda:
            self.frame = torch.ones((1, 1,4), dtype=torch.uint8)
            self.frame = self.frame.cuda()
            self.frame[:,:,3] = 1 # set alpha
        else:
            self.frame = np.ones((1, 1,4), dtype=np.uint8)

        self.enable_setup = True

        self.setupUi()

    def setupUi(self,):
        # 隐藏窗口边框
        # self.setWindowFlag(Qt.FramelessWindowHint, True)
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowTitle("DisplayDevice")
        self.setObjectName("DisplayDevice")
        # 设置外边距
        self.setContentsMargins(0,0,0,0)

    def playOnCuda(self):
        self.is_cuda = True

    def playOnCpu(self):
        self.is_cuda = False


    def setup(self, tex_size:list):
        """
            tex_size(list):
                [ w, h]
        """
        self.makeCurrent()
        self.tex_size = tex_size
        
        # self.show()
        # self.ctx.makeCurrent(self.ctx.surface())
        # print(f"self.context: {self.context()} \nself.ctx: {self.ctx}")
        # print(self.isValid())
        self.frame = torch.ones((tex_size[1], tex_size[0],4), dtype=torch.uint8)
        self.frame = self.frame.cuda()
        self.frame[:,:,3] = 1 # set alpha
        self.tex, self.cuda_buffer = self.create_shared_texture(tex_size[0], tex_size[1])
        print(self.cuda_buffer)
        self.program = gloo.Program(vertex = self.VERTEX_CODE,
                                    fragment = self.FRAGMENT_CODE,
                                    count = 4
                                    )
        self.program['position'] = [(-1,+1), (-1,-1), (+1,+1), (+1,-1)]
        self.program['texcoord'] = [(0,0), (0,1), (1,0), (1,1)]
        self.program['scale'] = 1
        self.program['tex'] = self.tex


    @contextmanager
    def cuda_activate(self, img):
        """Context manager simplifying use of pycuda.gl.RegisteredImage"""
        self.makeCurrent()
        # self.ctx.makeCurrent(self.ctx.surface())
        # print(f"self.context: {self.context()} \nself.ctx: {self.ctx}")
        # print(self.isValid())
        mapping = img.map()
        yield mapping.array(0,0)
        mapping.unmap()

    def create_shared_texture(self, w, h, c=4,
            dtype=np.uint8,
            map_flags=graphics_map_flags.NONE
            ):
        """Create and return a Texture2D with gloo and pycuda views."""
        # import pycuda.gl.autoinit
        # import pycuda.gl
        # self.ctx.makeCurrent(self.ctx.surface())
        # self.ctx.makeCurrent()
        self.makeCurrent()
        # print(f"self.context: {self.context()} \nself.ctx: {self.ctx}")
        # print(self.isValid())
        tex = np.zeros((h,w,c), dtype).view(gloo.Texture2D)
        tex.activate() # force gloo to create on GPU
        tex.deactivate()
        cuda_buffer = pycuda.gl.RegisteredImage(
            int(tex.handle), tex.target, map_flags)
        return tex, cuda_buffer


    def paintGL(self):
        self.clear()
        v_x, v_y, v_w, v_h = self.getViewportSize()
        gl.glViewport(v_x, v_y, v_w, v_h)
        self.program.draw(gl.GL_TRIANGLE_STRIP)
        # super().paintGL()

    def paintEvent(self, e: QPaintEvent):
        if self.is_cuda:
            # print("on cuda")
            super().paintEvent(e)
        else:
            # print("on cpu")
            height, width, channel = self.frame.shape
            bytesPerLine = channel * width
            qImg = QImage(self.frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
            self.painter.begin(self)
            self.painter.setRenderHint(QPainter.Antialiasing, True)
            self.painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            self.painter.setWindow(0, 0, width, height)
            v_x, v_y, v_w, v_h = self.getViewportSize()
            self.painter.setViewport(v_x, v_y, v_w, v_h)
            self.painter.drawImage(QRect(0, 0, width, height), qImg)
            self.painter.end()
            # super().paintEvent(e)

    def getViewportSize(self, aspectRatio=-1, mode="auto"):
        """
            Args:
                aspectRatio(int): aspectRatio to be displayed. The default value is - 1, which means the aspect ratio of the frame is used
                mode(str): mode to be displayed. 
        """
        height, width, _ = self.frame.shape
        # print(self.curr_frame.shape)
        if aspectRatio == -1:
            aspectRatio = 1.0 * width / height
        if mode == "auto":
            
            v_h = 0
            v_w = 0
            if aspectRatio*self.height()>self.width():
                v_h = round(self.width() / aspectRatio)
                v_w = self.width()
            else:
                v_h = self.height()
                v_w = round(self.height() * aspectRatio)
            v_x = round((self.width() - v_w) / 2.0)
            v_y = round((self.height() - v_h) / 2.0)
            return v_x, v_y, v_w, v_h
        
        return 0,0,width,height
        

    def clear(self):
        # self.makeCurrent()
        """ Clear the whole window """
        gl.glClearColor(*(0,0,0,1))
        gl.glClear(16640)


    def mapping_frame(self, frame:torch.Tensor):
        # import pycuda.gl.autoinit

        h,_ = self.tex.shape[:2]
        # copy from torch into buffer
        assert self.tex.nbytes == frame.numel()*frame.element_size()
        # print(self.cuda_buffer)
        with self.cuda_activate(self.cuda_buffer) as ary:
            cpy = pycuda.driver.Memcpy2D()
            cpy.set_src_device(frame.data_ptr())
            cpy.set_dst_array(ary)
            cpy.width_in_bytes = cpy.src_pitch = cpy.dst_pitch = self.tex.nbytes//h
            cpy.height = h
            cpy(aligned=False) # must on cuda
            torch.cuda.synchronize()
        

    def update(self, frame):
        assert isinstance(frame,np.ndarray) or isinstance(frame,torch.Tensor)
        """
            shape like this: [h , w , c] uint8 RGB image.
            if frame is torch.Tensor then frame should be a cuda tensor
        """
        # start=perf_counter()
        if isinstance(frame,torch.Tensor):
            # self.frame=frame.cuda().byte().contiguous()
            # torch.cuda.synchronize()
            if self.enable_setup:
                self.enable_setup = False
                self.is_cuda = True
                if self.tex is not None:
                    if self.tex.shape[0] != frame.shape[1] or \
                        self.tex.shape[1] != frame.shape[0]:
                        self.setup([frame.shape[1],frame.shape[0]])
                else:
                    self.setup([frame.shape[1],frame.shape[0]])
            self.frame = frame.byte().contiguous()
            self.mapping_frame(self.frame)

        elif isinstance(frame,np.ndarray):
            if not self.enable_setup:
                self.enable_setup = True
                self.is_cuda = False
            self.frame = frame

        super().update()
        # print((perf_counter()-start)*1000)


    def get_window(self):
        return self
# global flag
flag = True
def switcher():
    global flag
    if flag:
        print("playOnCpu")
        flag = False
        # dd.playOnCpu()
        # dd.setup([1920,1080])
        dd.update(img)
    else:
        print("playOnCuda")
        flag = True
        # dd.playOnCuda()
        # dd.setup([1920,1080])
        dd.update(frame_buffer)

def main():
    global img 
    global frame_buffer
    global dd
    img = cv2.imread("C:\\Users\\White\\Project\\rtsr_client_pyqt\\assets\\1080.png")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    frame_buffer = torch.from_numpy(img).type(torch.uint8)
    ones = torch.ones((frame_buffer.shape[0],frame_buffer.shape[1],1), dtype=torch.uint8)
    frame_buffer = torch.cat([frame_buffer,ones], dim=2)
    # self.frame_buffer:torch.Tensor = torch.ones((512,512,4),dtype=torch.uint8)
    frame_buffer = frame_buffer.cuda()
    torch.cuda.synchronize()
    app = QApplication(sys.argv)
    dd = DisplayDevice()
    timer = QTimer(dd)
    timer.timeout.connect(switcher)
    timer.start(20)
    dd.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
