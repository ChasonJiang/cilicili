

from enum import Enum, unique

@unique
class SRStatusCode(Enum):
    Started = 1
    IoError = 2
    LoadInferencerFailed = 3
    WaitBuffer = 4
    BufferFull = 5
    Quit = 6
    DecoderInitFailed = 7
    DecoderInitSuccess = 8
    LoadInferencerInfoFailed = 9
    ProcessException = 10
    InferredLoaded = 11

