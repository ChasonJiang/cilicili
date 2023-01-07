import sys
import pycuda.autoinit
import pycuda.driver as cuda
import pycuda.gl as cuda_gl
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets, QtOpenGL
from OpenGL import GL
from OpenGL.GLU import *
from OpenGL.GLUT import *


class GLWidget(QtWidgets.QOpenGLWidget):
    def __init__(self, parent):
        QtWidgets.QOpenGLWidget.__init__(self, parent)


        # Create a texture ID
        # self.texture_id = GL.glGenTextures(1)
    def init(self):
        textureId = (GL.GLuint * 1)()
        GL.glGenTextures(1, textureId)
        self.texture_id = textureId[0]

        # Bind the texture ID
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)

        # Set the texture parameters
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

        # Create a PyCUDA context for the texture
        self.texture_context = cuda_gl.BufferObject(int(self.texture_id))

    def paintGL(self):
        # self.init()
        # Clear the screen
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Enable 2D textures
        GL.glEnable(GL.GL_TEXTURE_2D)

        # Bind the texture
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)

        # Copy the GPU tensor to the texture using PyCUDA
        cuda_gl.register_buffer(self.gpu_tensor, self.texture_context)
        cuda_gl.copy_array_to_buffer(self.gpu_tensor, self.texture_context)
        cuda_gl.unregister_buffer(self.texture_context)

        # Draw a quad with the texture
        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2f(0.0, 0.0)
        GL.glVertex2f(-1.0, -1.0)
        GL.glTexCoord2f(1.0, 0.0)
        GL.glVertex2f(1.0, -1.0)
        GL.glTexCoord2f(1.0, 1.0)
        GL.glVertex2f(1.0, 1.0)
        GL.glTexCoord2f(0.0, 1.0)
        GL.glVertex2f(-1.0, 1.0)
        GL.glEnd()

        # Disable 2D textures
        GL.glDisable(GL.GL_TEXTURE_2D)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        # Create a GLWidget and set it as the central widget
        self.glWidget = GLWidget(self)
        self.setCentralWidget(self.glWidget)

        # Create a GPU tensor and assign it to the GLWidget
        self.gpu_tensor = cuda.gpuarray.to_gpu(np.random.rand(100, 100, 3).astype(np.float32))
        self.glWidget.gpu_tensor = self.gpu_tensor

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
