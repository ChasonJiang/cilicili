import os
import sys
from time import perf_counter, sleep
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *
# from PyQt5 import QtOpenGL
import PySide2
import cv2
from glumpy import gloo, transforms, app as glumpy_app
import torch
# torch.cuda.is_available()
# torch.tensor([1,1]).cuda()
# os.environ['__NV_PRIME_RENDER_OFFLOAD'] ="1"
# os.environ['__GLX_VENDOR_LIBRARY_NAME']="nvidia"
# os.environ['CUDA_DEVICE'] = "0"
# import pycuda.autoinit
# import pycuda.gl.autoinit
# import pycuda.gl
import pycuda.driver
# from PySide2.QtGui import QOpenGLFunctions
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from pycuda.gl import graphics_map_flags
from contextlib import contextmanager
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
# glActiveTexture(GL_TEXTURE_2D)
# a=glGenTextures(1)
glumpy_app.use("qt5")
class test(QOpenGLWidget,QOpenGLFunctions):
# class test(QtOpenGL.QGLWidget):

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
    def __init__(self, tex_size:list=None,is_cuda=False):
        super(test, self).__init__()
        # self.setWindowFlag(Qt.FramelessWindowHint, True)
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        # self.resize(0, 0)

        # self.context = QtOpenGL.QGLContext(QtOpenGL.QGLFormat())
        # self.makeCurrent()
        # self.setAutoBufferSwap(False)
        self.setMouseTracking(True)
        self._native_window= self
        self.native_window= self

        self.painter = QPainter()

        self.program = None
        self.cuda_buffer = None
        self.tex = None
        self.is_cuda=is_cuda
        self.frame = None
        if self.is_cuda:
            self.frame = torch.ones((1, 1,4), dtype=torch.uint8)
            self.frame = self.frame.cuda()
            self.frame[:,:,3] = 1 # set alpha
        else:
            self.frame = np.ones((1, 1,4), dtype=np.uint8)
        # self.frame = self.frame.cuda()
        # self.frame[:,:,3] = 1 # set alpha
        # self.device=torch.device("cuda")
        
        if tex_size is not None:
            self.setup(tex_size)
        
        # self.initializeOpenGLFunctions()
        # self.ctx= QOpenGLContext()
        # # arr = np.ones([1080,1920,4],dtype=np.uint8).view(0x0DE1)
        # handl=self.ctx.functions().glGenTextures(1,GL_TEXTURE_2D)
        # print(handl)
        
        
        # self.makeCurrent()
        # print(self.isValid())
        
        
        
        
            
        # gl.glViewport(0, 0, 0, 0)
        # self.setGeometry(0,0,0,0)

    def setOnCuda(self):
        self.is_cuda = True

    def setOnCpu(self):
        self.is_cuda = False

    def setup(self, tex_size:list):
        """
            tex_size(list):
                [ w, h]
        """
        # self.initializeOpenGLFunctions()
        glClearColor(0, 0, 0, 0);   
        glEnable(GL_TEXTURE_2D);    
        print(self.isValid())
        self.makeCurrent()
        self.frame = torch.ones((tex_size[1], tex_size[0],4), dtype=torch.uint8)
        self.frame = self.frame.cuda()
        self.frame[:,:,3] = 1 # set alpha
        self.tex, self.cuda_buffer = self.create_shared_texture(tex_size[0], tex_size[1])
        self.program = gloo.Program(vertex = self.VERTEX_CODE,
                                    fragment = self.FRAGMENT_CODE,
                                    count = 4
                                    )
        self.program['position'] = [(-1,+1), (-1,-1), (+1,+1), (+1,-1)]
        self.program['texcoord'] = [(0,0), (0,1), (1,0), (1,1)]
        self.program['scale'] = 1
        self.program['tex'] = self.tex
        # self.program["viewport"] = transforms.Viewport(transform=True,viewport=(0,0,100,50))

    @contextmanager
    def cuda_activate(self, img):
        """Context manager simplifying use of pycuda.gl.RegisteredImage"""
        mapping = img.map()
        yield mapping.array(0,0)
        mapping.unmap()

    def create_shared_texture(self, w, h, c=4,
            dtype=np.uint8,
            map_flags=graphics_map_flags.WRITE_DISCARD
            ):
        """Create and return a Texture2D with gloo and pycuda views."""
        import CudaAutoInit
        import pycuda.gl as pycuda_gl
        # import pycuda.gl.autoinit
        # import pycuda.gl
        tex = np.zeros((h,w,c), dtype).view(gloo.Texture2D)
        tex.activate() # force gloo to create on GPU
        tex.deactivate()
        cuda_buffer = pycuda.gl.RegisteredImage(
            int(tex.handle), tex.target, map_flags)
        return tex, cuda_buffer

    def initializeGL(self):
        # super().initializeGL()
        # print(self.geometry())
        # self.setDisplayMode()
        # gl.glEnable(gl.GL_MULTISAMPLE)
        print("initializeGL")
        # self.ctx.makeCurrent(self)
        
        
    # def eventFilter(self, obj:QObject, e:QEvent) -> bool:
    #     if e.type() == QEvent.Type.Paint:
    #         if self.is_cuda:
    #             self.paintEvent_cuda(e)
    #             return True
    #         else:
    #             self.paintEvent_cpu(e)
    #             return True
    #     return super().eventFilter(obj, e)

    # def resizeGL(self, w: int, h: int):
    #     super().resizeGL(w, h)
    #     self.setDisplayMode()

    def paintGL(self):
        if self.is_cuda:
            self.clear()
            self.program.draw(gl.GL_TRIANGLE_STRIP)
        else:
            super().paintGL()

    def paintEvent(self, e: QPaintEvent):
        if self.is_cuda:
            super().paintEvent(e)
        else:
            height, width, channel = self.frame.shape
            bytesPerLine = channel * width
            qImg = QImage(self.frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
            self.painter.begin(self)
            self.painter.setRenderHint(QPainter.Antialiasing, True)
            self.painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
            # self.setDisplayMode()
            self.painter.setWindow(0, 0, width, height)
            v_x, v_y, v_w, v_h = self.getViewportSize()
            self.painter.setViewport(v_x, v_y, v_w, v_h)
            self.painter.drawImage(QRect(0, 0, width, height), qImg)
            self.painter.end()

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


    def resizeEvent(self, e: QResizeEvent):
        super().resizeEvent(e)
        if self.is_cuda:
            v_x, v_y, v_w, v_h = self.getViewportSize()
            gl.glViewport(v_x, v_y, v_w, v_h)
        

    def clear(self):
        """ Clear the whole window """
        gl.glClearColor(*(0,0,0,1))
        gl.glClear(16640)

    def swap(self):
        self.swapBuffers()

    def activate(self):
        self.makeCurrent()

    def process(self):
        self.activate()
        self.paintGL()
        self.swap()

    def mapping_frame(self, frame:torch.Tensor):
        h,_ = self.tex.shape[:2]
        # copy from torch into buffer
        assert self.tex.nbytes == frame.numel()*frame.element_size()
        with self.cuda_activate(self.cuda_buffer) as ary:
            cpy = pycuda.driver.Memcpy2D()
            cpy.set_src_device(frame.data_ptr())
            cpy.set_dst_array(ary)
            cpy.width_in_bytes = cpy.src_pitch = cpy.dst_pitch = self.tex.nbytes//h
            cpy.height = h
            cpy(aligned=False) # must on cuda
            torch.cuda.synchronize()

    def update(self, frame):
        # print("2 update")
        assert isinstance(frame,np.ndarray) or isinstance(frame,torch.Tensor)
        """
            shape like this: [h , w , c] uint8 RGB image.
        """
        # start=perf_counter()
        if isinstance(frame,torch.Tensor):
            self.frame = frame.byte().contiguous()
            self.mapping_frame(self.frame)

        elif isinstance(frame,np.ndarray):
            self.frame = frame
        
        # self.process()
        super().update()
        # print((perf_counter()-start)*1000)


    def get_window(self):
        return self
    # def paintGL(self) -> None:
    #     return super().paintGL()

    # def closeEvent(self,e:QCloseEvent) -> None:
    #     print("asdf")
    #     pycuda_gl_autoinit.context.pop()
    #     return super().closeEvent(e)
    

    # def deleteLater(self):
    #     # import pycuda.gl.autoinit
    #     # import pycuda.gl
    #     print("asdf")
    #     pycuda_gl_autoinit.context.pop()
    #     return super().deleteLater()


class Device():

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


    def __init__(self, tex_size:list = None):
        
        self.window = glumpy_app.Window()
        # only qt5 of backend is supported
        self.native_window:QWidget =self.window._native_window
        # self.native_window.setWindowFlag(Qt.FramelessWindowHint, True)
        # self.native_window.setAttribute(Qt.WA_TranslucentBackground, True)
        # self.native_window.resize(0,0)
        # self.native_window.hide()
        self.window.set_handler("on_draw", self.on_draw)
        self.window.set_handler("on_close", self.on_close)
        

        self.screen = None
        self.cuda_buffer = None
        self.tex = None
        self.frame:torch.Tensor = None
        self.device=torch.device("cuda")
        # self.twice:int = 0
        if tex_size is not None:
            self.setup(tex_size)

    def setup(self, tex_size:list):
        """
            tex_size(list):
                [ w, h]
        """
        self.frame = torch.ones((tex_size[0], tex_size[1],4), dtype=torch.uint8)*1
        self.frame = self.frame.cuda()
        self.frame[:,:,3] = 1 # set alpha
        self.tex, self.cuda_buffer = self.create_shared_texture(tex_size[0], tex_size[1])
        self.screen = gloo.Program(vertex = self.VERTEX_CODE,
                                    fragment = self.FRAGMENT_CODE,
                                    count = 4
                                    )
        self.screen['position'] = [(-1,-1), (-1,+1), (+1,-1), (+1,+1)]
        self.screen['texcoord'] = [(0,0), (0,1), (1,0), (1,1)]
        self.screen['scale'] = 1
        self.screen['tex'] = self.tex
        # self.screen["viewport"] = transforms.Viewport(transform=True,viewport=(0,0,100,50))
        

    @contextmanager
    def cuda_activate(self, img):
        """Context manager simplifying use of pycuda.gl.RegisteredImage"""
        mapping = img.map()
        yield mapping.array(0,0)
        mapping.unmap()

    def create_shared_texture(self, w, h, c=4,
            dtype=np.uint8,
            map_flags=graphics_map_flags.WRITE_DISCARD
            ):
        """Create and return a Texture2D with gloo and pycuda views."""
        import pycuda.gl.autoinit
        import pycuda.gl
        tex = np.zeros((h,w,c), dtype).view(gloo.Texture2D)
        tex.activate() # force gloo to create on GPU
        tex.deactivate()
        cuda_buffer = pycuda.gl.RegisteredImage(
            int(tex.handle), tex.target, map_flags)
        return tex, cuda_buffer

    def on_draw(self, dt):
        # print("drawing")
        # print("asdfsadf")
        # if not self.twice:
        #     self.first = False
        #     return
        print(f"size: {self.window.get_size()} | position: {self.window.get_position()}")
        print(f"frame size: {self.frame.shape}")
        print(self.window._clearflags)
        h,_ = self.tex.shape[:2]
        # copy from torch into buffer
        assert self.tex.nbytes == self.frame.numel()*self.frame.element_size()
        with self.cuda_activate(self.cuda_buffer) as ary:
            cpy = pycuda.driver.Memcpy2D()
            cpy.set_src_device(self.frame.data_ptr())
            cpy.set_dst_array(ary)
            cpy.width_in_bytes = cpy.src_pitch = cpy.dst_pitch = self.tex.nbytes//h
            cpy.height = h
            cpy(aligned=True) # must on cuda
            torch.cuda.synchronize()
        # draw to screen
        self.window.clear()
        self.screen.draw(gl.GL_TRIANGLE_STRIP)

    def on_close(self):
        # import pycuda.gl.autoinit
        # import pycuda.gl.autoinit
        # import pycuda.gl
        pycuda.gl.autoinit.context.pop()

    def update(self, frame:torch.Tensor):
        # print("2 update")
        """
            shape like this: [h , w , c]
        """
        
        self.frame = frame.byte().contiguous()
        glumpy_app.__backend__.process(0)

    def get_window(self):
        self.window._native_window
        return self.window._native_window
        

class DisplayDevice(QWidget):
    def __init__(self, *args, **kwargs):
        super(DisplayDevice, self).__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.device=torch.device("cuda:0")
        img = cv2.imread("C:\\Users\\White\\Project\\rtsr_client_pyqt\\assets\\1080.png")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.img = img
        # img = np.ones((100, 100, 3), dtype=np.uint8)*100
        # self.glumpy_window = Device([img.shape[1], img.shape[0]])
        self.glumpy_window = test()
        self.glumpy_window.setOnCuda()
        self.glumpy_window.setup([img.shape[1], img.shape[0]])
        self.setup()
        # self.installEventFilter(self.glumpy_window.native_window)
        # self.glumpy_window.native_window.installEventFilter(self)
        # self.glumpy_window.window.set_size(512,512)
        self.frame_buffer = torch.from_numpy(img).type(torch.uint8)
        ones = torch.ones((self.frame_buffer.shape[0],self.frame_buffer.shape[1],1), dtype=torch.uint8)
        self.frame_buffer = torch.cat([self.frame_buffer,ones], dim=2)
        # self.frame_buffer:torch.Tensor = torch.ones((512,512,4),dtype=torch.uint8)
        self.frame_buffer = self.frame_buffer.cuda()
        torch.cuda.synchronize()
        print(torch.cuda.is_available())
        print(self.frame_buffer.device)
        print(self.frame_buffer.shape)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        
        
        # self.frame_buffer[:,:,3] = 1 # set alpha

    # def eventFilter(self, weight:QObject, event:QEvent) -> bool:
    #     if weight == self.glumpy_window.native_window:
    #         # print("eventFilter")
    #         event_type = event.type()
    #         if event_type == QEvent.Type.MouseMove:
    #             super().mouseMoveEvent(event)
    #             return True
    #         elif event_type == QEvent.Type.MouseButtonPress:
    #             super().mousePressEvent(event)
    #             return True
    #         # elif event_type == QEvent.Type.Resize:
    #         #     self.glumpy_window.resizeEvent(event)
    #         #     self.glumpy_window.update(self.frame_buffer)
    #             # print("Resize")

    #             return True
             
    #     return super().eventFilter(weight, event)

    counter=0
    def update(self):
        self.counter+=1
        if self.counter==100000:
            self.timer.stop()
            pycuda_gl_autoinit.context.pop()
            self.close()
        super().update()
        # print("sadfsd")
        self.glumpy_window.update(self.frame_buffer)
        


    # def paintEvent(self, event):
    #     print("paintEvent")
    #     return super().paintEvent(event)

    # def mouseMoveEvent(self, e):
    #     print("mouseMoveEvent")
    #     return super().mouseMoveEvent(e)

    # def mousePressEvent(self, e):
    #     print("mouse pressed")
    #     return super().mousePressEvent(e)
    
    # def resizeEvent(self, e):
    #     print("resizeEvent")
    #     return super().resizeEvent(e)

    def setup(self,):
        self.setObjectName("CiliCiliPlayer")
        self.resize(800, 640)
        self.setMinimumSize(QSize(480, 270))
        self.setStyleSheet("*{\n"
                            "background-color: rgba(0,0,0,0);\n"
                            "}")
        self.horizontalLayout = QHBoxLayout(self)
        # self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        # self.horizontalLayout.setSpacing(0)
        # self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.addWidget(self.glumpy_window.get_window(), stretch=1)
    #     self.retranslateUi()
    #     QMetaObject.connectSlotsByName(self)

    # def retranslateUi(self):
    #     _translate = QCoreApplication.translate
    #     self.setWindowTitle(_translate("CiliCiliPlayer", "Form"))

    # def show(self):
    #     self.timer = QTimer(self)
    #     self.timer.timeout.connect(self.update)
    #     self.timer.start(20)
        # super().show()

def main():
    app = QApplication(sys.argv)
    dd = DisplayDevice()
    
    dd.timer.start(1)
    dd.show()
    # dd.update()
    # dd.update()
    # print("opksadf")
    # while True:
    #     dd.update()
    #     sleep(0.1)
    #     glumpy_app.__backend__.process(0)
        
    
    #     glumpy_app.__backend__.process(0)
    # glumpy_app.run(framerate=10)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
