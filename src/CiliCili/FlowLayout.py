from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
class FlowLayout(QLayout):
    items=[]
    hSpace = -1
    vSpace = -1
    margin = -1
    def __init__(self, parent = None, margin = -1, hSpace = -1, vSpace = -1, limit_columns=5):
        # super(FlowLayout, self).__init__(parent=parent)
        super(FlowLayout,self).__init__(parent)
        # super().__init__(parent)
        self.vSpace = vSpace
        self.hSpace = hSpace
        self.margin = margin
        self.limit_columns = limit_columns
        self.setParent(parent)
        # self.setSpacing(0)
        self.setContentsMargins(margin,margin,margin,margin)

    def count(self):
        return len(self.items)

    # def addWidget(self, w: QWidget) -> None:
    #     # print(w)
    #     self.addItem(QWidgetItem(w))

    def addItem(self, item: QLayoutItem):
        self.items.append(item)

    def horizontalSpacing(self,):
        if (self.hSpace >= 0):
            return self.hSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutHorizontalSpacing)
        
    def verticalSpacing(self,):
        if (self.vSpace >= 0):
            return self.vSpace
        else:
            return self.smartSpacing(QStyle.PM_LayoutVerticalSpacing)

    def smartSpacing(self, pm:QStyle.PixelMetric):
        if self.parent() is not None:
            return -1
        elif (self.parent().isWidgetType()):
            pw:QWidget = self.parent()
            return pw.style().pixelMetric(pm, None, pw)
        else:
            return self.parent().spacing()

    # return
    def itemAt(self, index: int) :
        if index >= 0 and index < len(self.items):
            return self.items[index]
        else:
            return None
    
    # remove and return
    def takeAt(self, index: int) -> QLayoutItem:
        if index >= 0 and index < len(self.items):
            return self.items.pop(index)
        else:
            return None

    def clear(self):
        for item in self.items.copy():
            self.removeWidget(item.widget())

    def expandingDirections(self,):
        return 0

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        # if len(self.items)<=0:
        #     return width
        height = self.doLayout(QRect(0, 0, width, 0), False)
        return height

    def setGeometry(self, rect:QRect):
        
        super().setGeometry(rect)
        if len(self.items)<=0:
            return 
        # print(rect)
        # print("setGeometry: ", rect)
        self.doLayout(rect, True)

    def sizeHint(self,):
        return self.minimumSize()

    def minimumSize(self,):
        size=QSize()
        for item in self.items:
            size = size.expandedTo(item.minimumSize())
            # size = size.expandedTo(QSize(242,222))
        left, top, right, bottom=self.getContentsMargins()
        size += QSize(left+right, top+bottom)
        # size += QSize(self.horizontalSpacing(),self.verticalSpacing())
        return size

    def doLayout_bak(self, rect:QRect, is_scale:bool, threshold:int=1):
        left, top, right, bottom=self.getContentsMargins()
        effectiveRect:QRect = rect.adjusted(+left, +top, -right, -bottom)
        x:int = effectiveRect.x()
        y:int = effectiveRect.y()
        lineHeight:int = 0
        
        for item in self.items:
            assert isinstance(item,QLayoutItem)
            spaceX = self.horizontalSpacing()
            spaceY = self.verticalSpacing()

            nextX:int = x + item.sizeHint().width() + spaceX
            if (nextX - spaceX - effectiveRect.right() and lineHeight > 0):
                x = effectiveRect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX

            if is_scale:
                print(len(self.items))
                item.widget().setGeometry(QRect(QPoint(x, y), QSize(242, 222)))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        
        return y + lineHeight - rect.y() + bottom

    def doLayout(self, rect:QRect, is_scale:bool, threshold:int=1):
        if len(self.items)<=0:
            return 0

        left, top, right, bottom=self.getContentsMargins()
        effectiveRect:QRect = rect.adjusted(+left, +top, -right, -bottom)
        x_0:int = effectiveRect.x()
        y_0:int = effectiveRect.y()
        w:int = effectiveRect.width()

        x = x_0
        y = y_0
        item_width_limit = int((w-(self.limit_columns-1)*self.horizontalSpacing())/self.limit_columns)
        width_limit = item_width_limit
        
        spaceX:int = self.horizontalSpacing()
        spaceY:int = self.verticalSpacing()
        item = self.items[0]
        # item_aspect_ratio:float = item.sizeHint().width()/item.sizeHint().height()
        # item_min_width:int = item.sizeHint().width()
        item_aspect_ratio:float = 242/222
        item_min_width:int = 242
        # print(f"{item_min_width} > {item_width_limit}")
        if item_min_width-item_width_limit > threshold:
            width_limit = int((w-(self.limit_columns-1)*self.horizontalSpacing())/self.limit_columns)
            num_columns = self.limit_columns -1
            # width_limit = round((w-(num_columns-1)*self.horizontalSpacing())/num_columns)
            while num_columns!=0:
                width_limit = int((w-(num_columns-1)*self.horizontalSpacing())/num_columns)
                if width_limit>=item_min_width:
                    break
                else:
                    num_columns-=1
        height_limit = int(width_limit / item_aspect_ratio)

        for item in self.items:
            assert isinstance(item,QLayoutItem)
            nextX:int = x + width_limit + spaceX
            if (nextX - spaceX -effectiveRect.right() > threshold):
                x = x_0
                y = y + height_limit + spaceY
                nextX = x + width_limit + spaceX
            if is_scale:
                item.widget().setGeometry(QRect(QPoint(x, y), QSize(width_limit, height_limit)))

            x = nextX
        
        return y - y_0 + bottom + height_limit