from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def drawFunc():
    glClear(GL_COLOR_BUFFER_BIT)
    # glRotatef(1, 0, 1, 0)
    glutWireTeapot(0.5)
    glFlush()

glutInit()
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)

glutInitWindowSize(400, 400)

glutCreateWindow("First")
texture_id = glGenTextures(1)
print(texture_id)
glutDisplayFunc(drawFunc)

# glutIdleFunc(drawFunc)
glutMainLoop()
