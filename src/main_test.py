import functools
import sys
import asyncio
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from CiliCili.MainWindow import MainWindow

import qasync




async def main():
    def close_future(future, loop):
        loop.call_later(10, future.cancel)
        future.cancel()

    loop = asyncio.get_event_loop()
    future = asyncio.Future()

    app = QApplication.instance()
    if hasattr(app, "aboutToQuit"):
        getattr(app, "aboutToQuit").connect(
            functools.partial(close_future, future, loop)
        )

    mainWindow = MainWindow()
    mainWindow.show()

    await future
    return True

if __name__ == "__main__":
    try:
    # qasync.run(master())
    # m()
        qasync.run(main())
    except asyncio.exceptions.CancelledError:
        sys.exit(0)
