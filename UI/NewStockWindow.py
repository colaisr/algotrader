# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'NewStockWindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_newStockDlg(object):
    def setupUi(self, newStockDlg):
        if not newStockDlg.objectName():
            newStockDlg.setObjectName(u"newStockDlg")
        newStockDlg.resize(324, 370)
        self.gridLayout = QGridLayout(newStockDlg)
        self.gridLayout.setObjectName(u"gridLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(newStockDlg)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)

        self.txtTicker = QLineEdit(newStockDlg)
        self.txtTicker.setObjectName(u"txtTicker")

        self.horizontalLayout_2.addWidget(self.txtTicker)

        self.btnValidate = QPushButton(newStockDlg)
        self.btnValidate.setObjectName(u"btnValidate")
        self.btnValidate.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.btnValidate)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(newStockDlg)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.txtReason = QPlainTextEdit(newStockDlg)
        self.txtReason.setObjectName(u"txtReason")

        self.verticalLayout.addWidget(self.txtReason)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.buttonBox = QDialogButtonBox(newStockDlg)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)


        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)


        self.retranslateUi(newStockDlg)
        self.buttonBox.accepted.connect(newStockDlg.accept)
        self.buttonBox.rejected.connect(newStockDlg.reject)

        QMetaObject.connectSlotsByName(newStockDlg)
    # setupUi

    def retranslateUi(self, newStockDlg):
        newStockDlg.setWindowTitle(QCoreApplication.translate("newStockDlg", u"Dialog", None))
        self.label_2.setText(QCoreApplication.translate("newStockDlg", u"Ticker", None))
        self.btnValidate.setText(QCoreApplication.translate("newStockDlg", u"Validate", None))
        self.label.setText(QCoreApplication.translate("newStockDlg", u"Reason", None))
    # retranslateUi

