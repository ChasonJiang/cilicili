# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src\player\ui\PlayerControlLayer.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets

from .SeekSlider import SeekSlider


class Ui_playerControlLayer(object):
    def setupUi(self, playerControlLayer):
        playerControlLayer.setObjectName("playerControlLayer")
        playerControlLayer.resize(650, 402)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(playerControlLayer.sizePolicy().hasHeightForWidth())
        playerControlLayer.setSizePolicy(sizePolicy)
        playerControlLayer.setMinimumSize(QtCore.QSize(480, 270))
        playerControlLayer.setMaximumSize(QtCore.QSize(16777215, 16777215))
        playerControlLayer.setStyleSheet("*{\n"
"background-color: rgba(0,0,0,0);\n"
"}")
        self.verticalLayout = QtWidgets.QVBoxLayout(playerControlLayer)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.playStatusBar = QtWidgets.QFrame(playerControlLayer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.playStatusBar.sizePolicy().hasHeightForWidth())
        self.playStatusBar.setSizePolicy(sizePolicy)
        self.playStatusBar.setMinimumSize(QtCore.QSize(0, 300))
        self.playStatusBar.setStyleSheet("#playStatusBar {\n"
"background: qlineargradient(spread:pad, \n"
"x1:0, y1:0, \n"
"x2:0, y2:1, \n"
"stop:0 rgba(0, 0, 0, 80), \n"
"stop:0.3 rgba(0, 0, 0, 35), \n"
"stop:1 rgba(0, 0, 0, 0)\n"
");\n"
"}")
        self.playStatusBar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.playStatusBar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.playStatusBar.setLineWidth(0)
        self.playStatusBar.setObjectName("playStatusBar")
        self.verticalLayout.addWidget(self.playStatusBar)
        spacerItem = QtWidgets.QSpacerItem(17, 584, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.playControlBar = QtWidgets.QFrame(playerControlLayer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.playControlBar.sizePolicy().hasHeightForWidth())
        self.playControlBar.setSizePolicy(sizePolicy)
        self.playControlBar.setMinimumSize(QtCore.QSize(0, 102))
        self.playControlBar.setMaximumSize(QtCore.QSize(16777215, 100))
        self.playControlBar.setStyleSheet("#playControlBar {\n"
"background: qlineargradient(spread:pad, \n"
"x1:0, y1:0, \n"
"x2:0, y2:1, \n"
"stop:0 rgba(0, 0, 0, 0), \n"
"stop:0.3 rgba(0, 0, 0, 30), \n"
"stop:0.6 rgba(0, 0, 0, 90), \n"
"stop:1 rgba(0, 0, 0,150)\n"
");\n"
"padding-left:10px;\n"
"padding-right:10px;\n"
"\n"
"}")
        self.playControlBar.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.playControlBar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.playControlBar.setObjectName("playControlBar")
        self.playControlBarLayout = QtWidgets.QVBoxLayout(self.playControlBar)
        self.playControlBarLayout.setContentsMargins(0, 0, 0, 0)
        self.playControlBarLayout.setSpacing(0)
        self.playControlBarLayout.setObjectName("playControlBarLayout")
        self.seekSliderFrame = QtWidgets.QFrame(self.playControlBar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.seekSliderFrame.sizePolicy().hasHeightForWidth())
        self.seekSliderFrame.setSizePolicy(sizePolicy)
        self.seekSliderFrame.setMinimumSize(QtCore.QSize(0, 12))
        self.seekSliderFrame.setMaximumSize(QtCore.QSize(16777215, 10))
        self.seekSliderFrame.setStyleSheet("#playProgressFrame{\n"
"margin:0px;\n"
"border:0px;\n"
"padding:0px;\n"
"background: rgba(0,0,0,0);\n"
"}")
        self.seekSliderFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.seekSliderFrame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.seekSliderFrame.setLineWidth(0)
        self.seekSliderFrame.setObjectName("seekSliderFrame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.seekSliderFrame)
        self.horizontalLayout.setContentsMargins(10, 0, 10, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.seekSlider = SeekSlider(self.seekSliderFrame)
        self.horizontalLayout.addWidget(self.seekSlider)
        self.playControlBarLayout.addWidget(self.seekSliderFrame)
        self.playControlFrame = QtWidgets.QFrame(self.playControlBar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.playControlFrame.sizePolicy().hasHeightForWidth())
        self.playControlFrame.setSizePolicy(sizePolicy)
        self.playControlFrame.setMinimumSize(QtCore.QSize(0, 90))
        self.playControlFrame.setMaximumSize(QtCore.QSize(16777215, 90))
        self.playControlFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.playControlFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.playControlFrame.setLineWidth(0)
        self.playControlFrame.setObjectName("playControlFrame")
        self.playControlFrameLayout = QtWidgets.QHBoxLayout(self.playControlFrame)
        self.playControlFrameLayout.setContentsMargins(0, 0, 0, 0)
        self.playControlFrameLayout.setSpacing(0)
        self.playControlFrameLayout.setObjectName("playControlFrameLayout")
        self.playControlLeftFrame = QtWidgets.QFrame(self.playControlFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.playControlLeftFrame.sizePolicy().hasHeightForWidth())
        self.playControlLeftFrame.setSizePolicy(sizePolicy)
        self.playControlLeftFrame.setMinimumSize(QtCore.QSize(0, 90))
        self.playControlLeftFrame.setMaximumSize(QtCore.QSize(16777215, 90))
        self.playControlLeftFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.playControlLeftFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.playControlLeftFrame.setLineWidth(0)
        self.playControlLeftFrame.setObjectName("playControlLeftFrame")
        self.playControlLeftFrameLayout = QtWidgets.QHBoxLayout(self.playControlLeftFrame)
        self.playControlLeftFrameLayout.setContentsMargins(20, 0, 20, 0)
        self.playControlLeftFrameLayout.setSpacing(10)
        self.playControlLeftFrameLayout.setObjectName("playControlLeftFrameLayout")
        self.playButton = QtWidgets.QPushButton(self.playControlLeftFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.playButton.sizePolicy().hasHeightForWidth())
        self.playButton.setSizePolicy(sizePolicy)
        self.playButton.setMinimumSize(QtCore.QSize(30, 30))
        self.playButton.setMaximumSize(QtCore.QSize(30, 30))
        self.playButton.setStyleSheet("#playButton{\n"
"image: url(:/play_control_bar/pause_btn.svg);\n"
"background-color: rgba(0,0,0,0);\n"
"padding:0;\n"
"border:0;\n"
"margin:0;\n"
"}\n"
"#playButton:checked{\n"
"image: url(:/play_control_bar/play_btn.svg);\n"
"background-color: rgba(0,0,0,0);\n"
"padding:0;\n"
"border:0;\n"
"margin:0;\n"
"}")
        self.playButton.setText("")
        self.playButton.setIconSize(QtCore.QSize(0, 0))
        self.playButton.setCheckable(True)
        self.playButton.setChecked(False)
        self.playButton.setObjectName("playButton")
        self.playControlLeftFrameLayout.addWidget(self.playButton)
        self.playProgressInfo = QtWidgets.QLineEdit(self.playControlLeftFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.playProgressInfo.sizePolicy().hasHeightForWidth())
        self.playProgressInfo.setSizePolicy(sizePolicy)
        self.playProgressInfo.setMinimumSize(QtCore.QSize(150, 25))
        self.playProgressInfo.setMaximumSize(QtCore.QSize(150, 25))
        self.playProgressInfo.setStyleSheet("#playProgressInfo{\n"
"background-color: rgba(0,0,0,0);\n"
"color:rgba(255, 255, 255, 230);\n"
"font-family: Microsoft YaHei;\n"
"font-size:18px;\n"
"border:0;\n"
"padding:0;\n"
"margin-left:5px;\n"
"margin-right:5px\n"
"}")
        self.playProgressInfo.setText("")
        self.playProgressInfo.setAlignment(QtCore.Qt.AlignCenter)
        self.playProgressInfo.setDragEnabled(False)
        self.playProgressInfo.setReadOnly(True)
        self.playProgressInfo.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.playProgressInfo.setObjectName("playProgressInfo")
        self.playControlLeftFrameLayout.addWidget(self.playProgressInfo)
        self.playControlFrameLayout.addWidget(self.playControlLeftFrame)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.playControlFrameLayout.addItem(spacerItem1)
        self.playControlRightFrame = QtWidgets.QFrame(self.playControlFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.playControlRightFrame.sizePolicy().hasHeightForWidth())
        self.playControlRightFrame.setSizePolicy(sizePolicy)
        self.playControlRightFrame.setMinimumSize(QtCore.QSize(0, 90))
        self.playControlRightFrame.setMaximumSize(QtCore.QSize(16777215, 90))
        self.playControlRightFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.playControlRightFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.playControlRightFrame.setLineWidth(0)
        self.playControlRightFrame.setObjectName("playControlRightFrame")
        self.playControlRightFrameLayout = QtWidgets.QHBoxLayout(self.playControlRightFrame)
        self.playControlRightFrameLayout.setContentsMargins(20, 0, 20, 0)
        self.playControlRightFrameLayout.setSpacing(30)
        self.playControlRightFrameLayout.setObjectName("playControlRightFrameLayout")
        self.superResolutionButton = QtWidgets.QPushButton(self.playControlRightFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.superResolutionButton.sizePolicy().hasHeightForWidth())
        self.superResolutionButton.setSizePolicy(sizePolicy)
        self.superResolutionButton.setMinimumSize(QtCore.QSize(0, 30))
        self.superResolutionButton.setMaximumSize(QtCore.QSize(16777215, 30))
        self.superResolutionButton.setStyleSheet("#superResolutionButton{\n"
"color:rgba(255,255,255,230);\n"
"font-family: Microsoft YaHei;\n"
"font-weight:bold;\n"
"font-size:20px;\n"
"background-color: rgba(0,0,0,0);\n"
"padding:0;\n"
"border:0;\n"
"margin:0;\n"
"}")
        self.superResolutionButton.setIconSize(QtCore.QSize(0, 0))
        self.superResolutionButton.setCheckable(True)
        self.superResolutionButton.setObjectName("superResolutionButton")
        self.playControlRightFrameLayout.addWidget(self.superResolutionButton)
        self.resolutionButton = QtWidgets.QPushButton(self.playControlRightFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.resolutionButton.sizePolicy().hasHeightForWidth())
        self.resolutionButton.setSizePolicy(sizePolicy)
        self.resolutionButton.setMinimumSize(QtCore.QSize(0, 30))
        self.resolutionButton.setMaximumSize(QtCore.QSize(16777215, 30))
        self.resolutionButton.setStyleSheet("#resolutionButton{\n"
"color:rgba(255,255,255,230);\n"
"font-family: Microsoft YaHei;\n"
"font-weight:bold;\n"
"font-size:20px;\n"
"background-color: rgba(0,0,0,0);\n"
"padding:0;\n"
"border:0;\n"
"margin:0;\n"
"}")
        self.resolutionButton.setCheckable(True)
        self.resolutionButton.setObjectName("resolutionButton")
        self.playControlRightFrameLayout.addWidget(self.resolutionButton)
        self.volumeButton = QtWidgets.QPushButton(self.playControlRightFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.volumeButton.sizePolicy().hasHeightForWidth())
        self.volumeButton.setSizePolicy(sizePolicy)
        self.volumeButton.setMinimumSize(QtCore.QSize(30, 30))
        self.volumeButton.setMaximumSize(QtCore.QSize(27, 32))
        self.volumeButton.setStyleSheet("#volumeButton{\n"
"image: url(:/play_control_bar/volume_btn.svg);\n"
"background-color: rgba(0,0,0,0);\n"
"padding:0;\n"
"border:0;\n"
"margin:0;\n"
"}\n"
"#volumeButton:checked{\n"
"image: url(:/play_control_bar/mute_btn.svg);\n"
"background-color: rgba(0,0,0,0);\n"
"padding:0;\n"
"border:0;\n"
"margin:0;\n"
"}")
        self.volumeButton.setText("")
        self.volumeButton.setIconSize(QtCore.QSize(0, 0))
        self.volumeButton.setObjectName("volumeButton")
        self.playControlRightFrameLayout.addWidget(self.volumeButton)
        self.settingButton = QtWidgets.QPushButton(self.playControlRightFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.settingButton.sizePolicy().hasHeightForWidth())
        self.settingButton.setSizePolicy(sizePolicy)
        self.settingButton.setMinimumSize(QtCore.QSize(32, 32))
        self.settingButton.setMaximumSize(QtCore.QSize(32, 32))
        self.settingButton.setStyleSheet("#settingButton{\n"
"image:url(:/play_control_bar/setting_btn.svg);\n"
"background-color: rgba(0,0,0,0);\n"
"padding:0;\n"
"border:0;\n"
"margin:0;\n"
"}")
        self.settingButton.setText("")
        self.settingButton.setIconSize(QtCore.QSize(0, 0))
        self.settingButton.setCheckable(True)
        self.settingButton.setObjectName("settingButton")
        self.playControlRightFrameLayout.addWidget(self.settingButton)
        self.fullScreenButton = QtWidgets.QPushButton(self.playControlRightFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fullScreenButton.sizePolicy().hasHeightForWidth())
        self.fullScreenButton.setSizePolicy(sizePolicy)
        self.fullScreenButton.setMinimumSize(QtCore.QSize(30, 30))
        self.fullScreenButton.setMaximumSize(QtCore.QSize(30, 30))
        self.fullScreenButton.setStyleSheet("#fullScreenButton{\n"
"image:url(:/play_control_bar/full_screen_btn.svg);\n"
"background-color: rgba(0,0,0,0);\n"
"padding:0;\n"
"border:0;\n"
"margin:0;\n"
"}\n"
"#fullScreenButton:checked{\n"
"image:url(:/play_control_bar/small_screen_btn.svg);\n"
"background-color: rgba(0,0,0,0);\n"
"padding:0;\n"
"border:0;\n"
"margin:0;\n"
"}")
        self.fullScreenButton.setText("")
        self.fullScreenButton.setIconSize(QtCore.QSize(0, 0))
        self.fullScreenButton.setCheckable(True)
        self.fullScreenButton.setObjectName("fullScreenButton")
        self.playControlRightFrameLayout.addWidget(self.fullScreenButton)
        self.playControlRightFrameLayout.setStretch(0, 1)
        self.playControlRightFrameLayout.setStretch(1, 1)
        self.playControlRightFrameLayout.setStretch(2, 1)
        self.playControlRightFrameLayout.setStretch(3, 1)
        self.playControlRightFrameLayout.setStretch(4, 1)
        self.playControlFrameLayout.addWidget(self.playControlRightFrame)
        self.playControlBarLayout.addWidget(self.playControlFrame)
        self.verticalLayout.addWidget(self.playControlBar)

        self.retranslateUi(playerControlLayer)
        QtCore.QMetaObject.connectSlotsByName(playerControlLayer)

    def retranslateUi(self, playerControlLayer):
        _translate = QtCore.QCoreApplication.translate
        playerControlLayer.setWindowTitle(_translate("playerControlLayer", "Form"))
        self.playProgressInfo.setPlaceholderText(_translate("playerControlLayer", "00:00 / 00:00"))
        self.superResolutionButton.setText(_translate("playerControlLayer", "超分辨率"))
        self.resolutionButton.setText(_translate("playerControlLayer", "清晰度"))
from .PlayerAssets import *