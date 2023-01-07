import sys
from PyQt5 import QtGui, QtCore, QtWidgets, QtOpenGL
from OpenGL import GL
import cv2

QtOpenGL.QGLFormat.setDefaultFormat(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers))


class GLWidget(QtWidgets.QOpenGLWidget, QtWidgets.QOpenGLExtraFunctions):
    def __init__(self, parent):
        QtWidgets.QOpenGLWidget.__init__(self, parent)

        self.image = None

        # Create a texture ID
        self.texture_id = GL.glGenTextures(1)

        # Bind the texture ID
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)

        # Set the texture parameters
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)

    def paintGL(self):
        # Clear the screen
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Enable 2D textures
        GL.glEnable(GL.GL_TEXTURE_2D)

        # Bind the texture
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture_id)

        # Copy the image data to the texture using OpenGL
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGB, self.image.shape[1], self.image.shape[0], 0, GL.GL_BGR, GL.GL_UNSIGNED_BYTE, self.image)

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

        # Load the image
        self.image = cv2.imread("img.png")

        # Create a GLWidget and set it as the central widget
        glWidget = GLWidget(self)
        self.setCentralWidget(glWidget)

        # Assign the image to the GLWidget
        glWidget.image = self.image

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
