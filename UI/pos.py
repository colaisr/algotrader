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
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
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


        self.horizontalLayout_2.addLayout(self.bulck_data)

        self.gg = QGridLayout()
        self.gg.setObjectName(u"gg")

        self.horizontalLayout_2.addLayout(self.gg)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_4)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lProfitP = QLabel(self.border_frame)
        self.lProfitP.setObjectName(u"lProfitP")

        self.horizontalLayout.addWidget(self.lProfitP)

        self.label_2 = QLabel(self.border_frame)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_5)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.gridLayout_2.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)


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

