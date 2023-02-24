



class HandlerCmd():
    Quit = 1
    Start = 2
    Switch = 3
    QuitSRWorker = 4
    QuitSRThread = 5
    LoadInferencer = 6
    def __init__(self, cmd:int, args=None):
        assert cmd is not None
        self.cmd = cmd
        self.args = args

