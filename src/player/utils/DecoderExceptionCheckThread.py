import re
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class DecoderExceptionCheckThread(QObject):
    error_signal = pyqtSignal(str)
    def __init__(self, process):
        super(DecoderExceptionCheckThread, self).__init__()
        self.process = process
        self.unable_to_read = "Unable to read"
        self.io_error = "I/O error"
        self.broken_pipe = "Broken pipe"
        self.unknown_error = "Unknown error"

    def run(self):
        btyes=self.process.stderr.read()
        # print("sadfjkhsklj")
        # print(btyes)
        error = btyes.decode("utf-8")
        if re.search(self.io_error, error) is not None:
            self.error_signal.emit(self.io_error)
        elif re.search(self.io_error,error) is not None:
            self.error_signal.emit(self.unable_to_read)
        elif re.search(self.broken_pipe,error) is not None:
            self.error_signal.emit(self.broken_pipe)
        else:
            self.error_signal.emit(self.unknown_error)