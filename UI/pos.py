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
        position_canvas.resize(388, 179)
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
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.bulck_data = QVBoxLayout()
        self.bulck_data.setObjectName(u"bulck_data")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.bulck_data.addItem(self.verticalSpacer)

        self.lStock = QLabel(self.border_frame)
        self.lStock.setObjectName(u"lStock")
        self.lStock.setStyleSheet(u"color: rgb(0, 0, 255);")
        self.lStock.setAlignment(Qt.AlignCenter)

        self.bulck_data.addWidget(self.lStock)

        self.lVolume = QLabel(self.border_frame)
        self.lVolume.setObjectName(u"lVolume")
        self.lVolume.setAlignment(Qt.AlignCenter)

        self.bulck_data.addWidget(self.lVolume)

        self.lBulckValue = QLabel(self.border_frame)
        self.lBulckValue.setObjectName(u"lBulckValue")
        self.lBulckValue.setAlignment(Qt.AlignCenter)

        self.bulck_data.addWidget(self.lBulckValue)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.bulck_data.addItem(self.verticalSpacer_3)


        self.horizontalLayout_4.addLayout(self.bulck_data)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.gg = QGridLayout()
        self.gg.setObjectName(u"gg")

        self.horizontalLayout_4.addLayout(self.gg)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalSpacer_4 = QSpacerItem(20, 28, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_4)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")

        self.horizontalLayout.addLayout(self.horizontalLayout_2)

        self.lProfitP = QLabel(self.border_frame)
        self.lProfitP.setObjectName(u"lProfitP")

        self.horizontalLayout.addWidget(self.lProfitP)

        self.lp = QLabel(self.border_frame)
        self.lp.setObjectName(u"lp")

        self.horizontalLayout.addWidget(self.lp)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")

        self.horizontalLayout.addLayout(self.horizontalLayout_3)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.pbl = QHBoxLayout()
        self.pbl.setObjectName(u"pbl")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.pbl.addItem(self.horizontalSpacer_2)

        self.prgProfit = QProgressBar(self.border_frame)
        self.prgProfit.setObjectName(u"prgProfit")
        self.prgProfit.setValue(24)
        self.prgProfit.setOrientation(Qt.Vertical)
        self.prgProfit.setInvertedAppearance(False)

        self.pbl.addWidget(self.prgProfit)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.pbl.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.pbl)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_5)


        self.horizontalLayout_4.addLayout(self.verticalLayout_2)


        self.gridLayout_2.addLayout(self.horizontalLayout_4, 0, 0, 1, 1)


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
        self.lp.setText(QCoreApplication.translate("position_canvas", u"%", None))
    # retranslateUi

