

from enum import Enum, unique

@unique
class SRStatusCode(Enum):
    InferencerStarted = 1
    IoError = 2
    LoadInferencerError = 3
    WaitBuffer = 4
    BufferFull = 5
    Quit = 6

