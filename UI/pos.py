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
        position_canvas.resize(388, 88)
        position_canvas.setStyleSheet(u"border-color: rgb(153, 102, 51);")
        self.gridLayout = QGridLayout(position_canvas)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lStock = QLabel(position_canvas)
        self.lStock.setObjectName(u"lStock")
        self.lStock.setStyleSheet(u"color: rgb(0, 0, 255);")

        self.verticalLayout.addWidget(self.lStock)

        self.lVolume = QLabel(position_canvas)
        self.lVolume.setObjectName(u"lVolume")

        self.verticalLayout.addWidget(self.lVolume)


        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lProfitP = QLabel(position_canvas)
        self.lProfitP.setObjectName(u"lProfitP")

        self.horizontalLayout.addWidget(self.lProfitP)

        self.label_2 = QLabel(position_canvas)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.label_2)


        self.horizontalLayout_2.addLayout(self.horizontalLayout)


        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)


        self.retranslateUi(position_canvas)

        QMetaObject.connectSlotsByName(position_canvas)
    # setupUi

    def retranslateUi(self, position_canvas):
        position_canvas.setWindowTitle(QCoreApplication.translate("position_canvas", u"Form", None))
        self.lStock.setText(QCoreApplication.translate("position_canvas", u"STK", None))
        self.lVolume.setText(QCoreApplication.translate("position_canvas", u"-", None))
        self.lProfitP.setText(QCoreApplication.translate("position_canvas", u"-", None))
        self.label_2.setText(QCoreApplication.translate("position_canvas", u"%", None))
    # retranslateUi

