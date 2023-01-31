from contextlib import contextmanager
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
# from PySide2.QtGui import *
# from PySide2.QtCore import *
# from PySide2.QtWidgets import *
import OpenGL.GL as gl
import OpenGL.GLUT as glut
import cv2
import numpy as np
import torch
import pycuda.driver
from pycuda.gl import graphics_map_flags
from glumpy import gloo, transforms, gl as glumpy_gl, app as glumpy_app
glumpy_app.use("qt5")

class GLWidget(QOpenGLWidget):
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
    def __init__(self,parent=None):
        super(GLWidget, self).__init__(parent)
        # self.resize(512,512)
        # self.ctx = self.context()
        # self.gl = self.ctx.functions()
        # self.ctx.makeCurrent()
        # self.gl.initializeOpenGLFunctions()
        self.curr_frame = torch.ones((512,512,4),dtype=torch.uint8).cuda()*100
        
        
        
    def initializeGL(self) -> None:
        # self.initializeOpenGLFunctions()
        # self.context().functions().initializeOpenGLFunctions()
        # print(self.isValid())
        # print("asdfkj")
        self.ctx = self.context()
        # self.gl = self.ctx.functions()
        # self.ctx.makeCurrent()
        # self.gl.initializeOpenGLFunctions()
        self.setup([512,512])

    def setup(self, tex_size:list):
        """
            tex_size(list):
                [ w, h]
        """
        # self.initializeOpenGLFunctions()
        # gl.glClearColor(0, 0, 0, 0);   
        # gl.glEnable(gl.GL_TEXTURE_2D);    
        # print(self.isValid())
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
        import pycuda.gl.autoinit
        import pycuda.gl
        # import pycuda.gl.autoinit
        # import pycuda.gl
        tex = np.zeros((h,w,c), dtype).view(gloo.Texture2D)
        tex.activate() # force gloo to create on GPU
        tex.deactivate()
        cuda_buffer = pycuda.gl.RegisteredImage(
            int(tex.handle), tex.target, map_flags)
        return tex, cuda_buffer



    def paintGL(self) -> None:
        # gl.glClearColor(0.2,0.4,0.1,1)
        # # self.glClearColor(0.2,0.4,0.1,1)
        # gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        gl.glClearColor(*(0,0,0,1))
        gl.glClear(16640)
        self.program.draw(gl.GL_TRIANGLE_STRIP)


    def update(self):
        self.mapping_frame(self.curr_frame)
        super().update()

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


class DisplayDevice(QOpenGLWidget):
# class DisplayDevice(QtOpenGL.QGLWidget):

    setup_signal = pyqtSignal(list)

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

    def initializeGL(self):
        if self.is_cuda and self.tex_size is not None:
            self.setup(self.tex_size)

    def setup(self, tex_size:list):
        """
            tex_size(list):
                [ w, h]
        """
        # self.show()
        self.makeCurrent()
        # print(self.isValid())
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


    def paintGL(self):
        self.clear()
        v_x, v_y, v_w, v_h = self.getViewportSize()
        gl.glViewport(v_x, v_y, v_w, v_h)
        self.program.draw(gl.GL_TRIANGLE_STRIP)

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
        self.makeCurrent()
        """ Clear the whole window """
        gl.glClearColor(*(0,0,0,1))
        gl.glClear(16640)


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

        super().update()
        # print((perf_counter()-start)*1000)


    def get_window(self):
        return self



def main():
    img = cv2.imread("C:\\Users\\White\\Project\\rtsr_client_pyqt\\assets\\1080.png")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    frame_buffer = torch.from_numpy(img).type(torch.uint8)
    ones = torch.ones((frame_buffer.shape[0],frame_buffer.shape[1],1), dtype=torch.uint8)
    frame_buffer = torch.cat([frame_buffer,ones], dim=2)
    # self.frame_buffer:torch.Tensor = torch.ones((512,512,4),dtype=torch.uint8)
    frame_buffer = frame_buffer.cuda()
    torch.cuda.synchronize()
    app = QApplication(sys.argv)
    dd = DisplayDevice(tex_size=[1920,1080],is_cuda=True)
    dd.show()
    dd.update(frame_buffer)
    sys.exit(app.exec_())





class Window(QWidget):
    def __init__(self,parent=None):
        super(Window, self).__init__(parent=parent)
        img = cv2.imread("C:\\Users\\White\\Project\\rtsr_client_pyqt\\assets\\1080.png")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.img = img
        frame_buffer = torch.from_numpy(img).type(torch.uint8)
        ones = torch.ones((frame_buffer.shape[0],frame_buffer.shape[1],1), dtype=torch.uint8)
        frame_buffer = torch.cat([frame_buffer,ones], dim=2)
        # self.frame_buffer:torch.Tensor = torch.ones((512,512,4),dtype=torch.uint8)
        self.frame_buffer = frame_buffer.cuda()
        torch.cuda.synchronize()
        self.setupUi()

    def setupUi(self,):
        self.setObjectName("Form")
        self.resize(714, 647)
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.openGLWidget = DisplayDevice(self,tex_size=[1920,1080],is_cuda=False)
        self.openGLWidget.setObjectName("openGLWidget")
        self.horizontalLayout.addWidget(self.openGLWidget)

        self.retranslateUi()
        QMetaObject.connectSlotsByName(self)

    def retranslateUi(self,):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Form"))
    
    def update(self):
        self.openGLWidget.update(self.img)
        super().update()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    w = Window()
    w.show()
    w.update()

    # glw = GLWidget()
    # glw.show()
    # glw.update()

    sys.exit(app.exec_())
    # main()