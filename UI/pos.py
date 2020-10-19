# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pos.ui'
##
## Created by: Qt User Interface Compiler version 5.15.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_position_canvas(object):
    def setupUi(self, position_canvas):
        if not position_canvas.objectName():
            position_canvas.setObjectName(u"position_canvas")
        position_canvas.resize(388, 128)
        position_canvas.setStyleSheet(u"")
        self.gridLayout = QGridLayout(position_canvas)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(1, 1, 1, 1)
        self.border_frame = QFrame(position_canvas)
        self.border_frame.setObjectName(u"border_frame")
        self.border_frame.setFrameShape(QFrame.StyledPanel)
        self.border_frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.border_frame)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(3, 3, 3, 3)
        self.mainholder = QHBoxLayout()
        self.mainholder.setObjectName(u"mainholder")
        self.bulck_data = QVBoxLayout()
        self.bulck_data.setObjectName(u"bulck_data")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.bulck_data.addItem(self.verticalSpacer)

        self.lStock = QLabel(self.border_frame)
        self.lStock.setObjectName(u"lStock")
        self.lStock.setStyleSheet(u"color: rgb(0, 0, 255);")

        self.bulck_data.addWidget(self.lStock)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.bulck_data.addItem(self.verticalSpacer_2)

        self.lVolume = QLabel(self.border_frame)
        self.lVolume.setObjectName(u"lVolume")

        self.bulck_data.addWidget(self.lVolume)

        self.lBulckValue = QLabel(self.border_frame)
        self.lBulckValue.setObjectName(u"lBulckValue")

        self.bulck_data.addWidget(self.lBulckValue)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.bulck_data.addItem(self.verticalSpacer_3)


        self.mainholder.addLayout(self.bulck_data)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.mainholder.addItem(self.horizontalSpacer_2)

        self.scrollArea = QScrollArea(self.border_frame)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 91, 114))
        self.gridLayout_4 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gg = QGridLayout()
        self.gg.setObjectName(u"gg")

        self.gridLayout_4.addLayout(self.gg, 0, 0, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.mainholder.addWidget(self.scrollArea)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.mainholder.addItem(self.horizontalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lProfitP = QLabel(self.border_frame)
        self.lProfitP.setObjectName(u"lProfitP")

        self.horizontalLayout.addWidget(self.lProfitP)

        self.label_2 = QLabel(self.border_frame)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)


        self.mainholder.addLayout(self.horizontalLayout)


        self.gridLayout_2.addLayout(self.mainholder, 0, 0, 1, 1)


        self.gridLayout.addWidget(self.border_frame, 1, 0, 1, 1)


        self.retranslateUi(position_canvas)

        QMetaObject.connectSlotsByName(position_canvas)
    # setupUi

    def retranslateUi(self, position_canvas):
        position_canvas.setWindowTitle(QCoreApplication.translate("position_canvas", u"Form", None))
        self.lStock.setText(QCoreApplication.translate("position_canvas", u"STK", None))
        self.lVolume.setText(QCoreApplication.translate("position_canvas", u"-", None))
        self.lBulckValue.setText(QCoreApplication.translate("position_canvas", u"--", None))
        self.lProfitP.setText(QCoreApplication.translate("position_canvas", u"-", None))
        self.label_2.setText(QCoreApplication.translate("position_canvas", u"%", None))
    # retranslateUi

