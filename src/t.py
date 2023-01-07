from OpenGL import GL as gl
from OpenGL.GLU import *
from OpenGL.GLUT import *

def createEmptyTexture(width, height):
    textureId = (gl.GLuint * 1)()
    gl.glGenTextures(1, textureId)
    gl.glBindTexture(gl.GL_TEXTURE_2D, textureId[0])
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
    #None means reserve texture memory, but texels are undefined
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA8, width, height, 0, gl.GL_BGRA, gl.GL_UNSIGNED_BYTE, None)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    return textureId[0]


if __name__ == "__main__":
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(400, 400)
    glutCreateWindow("First")
    id = createEmptyTexture(1920, 1080)