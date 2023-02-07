from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class GLayout(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.item_list = []

    def addWidget(self, w: QWidget) -> None:
        # print(w)
        self.addItem(QWidgetItem(w))

    def addItem(self, item):
        self.item_list.append(item)

    def count(self):
        return len(self.item_list)

    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None

    def setGeometry(self, rect):
        x = rect.x()
        y = rect.y()
        for item in self.item_list:
            item.setGeometry(QRect(x, y, item.sizeHint().width(), item.sizeHint().height()))
            y = y + item.sizeHint().height() + 5