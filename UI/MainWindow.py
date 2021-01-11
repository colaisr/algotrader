# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1282, 772)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(600, 400))
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.splitter = QSplitter(self.centralwidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayout_4 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.general = QHBoxLayout()
        self.general.setObjectName(u"general")
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.lAcc = QLabel(self.layoutWidget)
        self.lAcc.setObjectName(u"lAcc")

        self.horizontalLayout.addWidget(self.lAcc)


        self.verticalLayout_7.addLayout(self.horizontalLayout)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_8 = QLabel(self.layoutWidget)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_6.addWidget(self.label_8)

        self.lMarketValue = QLabel(self.layoutWidget)
        self.lMarketValue.setObjectName(u"lMarketValue")

        self.horizontalLayout_6.addWidget(self.lMarketValue)


        self.verticalLayout_7.addLayout(self.horizontalLayout_6)


        self.general.addLayout(self.verticalLayout_7)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.label_7 = QLabel(self.layoutWidget)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_9.addWidget(self.label_7)

        self.lSma = QLabel(self.layoutWidget)
        self.lSma.setObjectName(u"lSma")

        self.verticalLayout_9.addWidget(self.lSma)


        self.general.addLayout(self.verticalLayout_9)

        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.label_9 = QLabel(self.layoutWidget)
        self.label_9.setObjectName(u"label_9")

        self.verticalLayout_10.addWidget(self.label_9)

        self.lPositionsTotalValue = QLabel(self.layoutWidget)
        self.lPositionsTotalValue.setObjectName(u"lPositionsTotalValue")

        self.verticalLayout_10.addWidget(self.lPositionsTotalValue)


        self.general.addLayout(self.verticalLayout_10)

        self.btnSettings = QPushButton(self.layoutWidget)
        self.btnSettings.setObjectName(u"btnSettings")
        self.btnSettings.setEnabled(False)

        self.general.addWidget(self.btnSettings)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.general.addItem(self.horizontalSpacer_2)

        self.lcdPNL = QLCDNumber(self.layoutWidget)
        self.lcdPNL.setObjectName(u"lcdPNL")
        self.lcdPNL.setFrameShape(QFrame.Box)
        self.lcdPNL.setFrameShadow(QFrame.Plain)
        self.lcdPNL.setLineWidth(2)
        self.lcdPNL.setMidLineWidth(0)

        self.general.addWidget(self.lcdPNL)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.general.addItem(self.horizontalSpacer)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout.addWidget(self.label_4)

        self.label_5 = QLabel(self.layoutWidget)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout.addWidget(self.label_5)


        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.lblTime = QLabel(self.layoutWidget)
        self.lblTime.setObjectName(u"lblTime")

        self.verticalLayout_2.addWidget(self.lblTime)

        self.lblMarket = QLabel(self.layoutWidget)
        self.lblMarket.setObjectName(u"lblMarket")

        self.verticalLayout_2.addWidget(self.lblMarket)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)


        self.general.addLayout(self.horizontalLayout_3)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.chbxProcess = QCheckBox(self.layoutWidget)
        self.chbxProcess.setObjectName(u"chbxProcess")
        self.chbxProcess.setEnabled(False)

        self.verticalLayout_3.addWidget(self.chbxProcess)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(self.layoutWidget)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.lblAvailTrades = QLabel(self.layoutWidget)
        self.lblAvailTrades.setObjectName(u"lblAvailTrades")

        self.horizontalLayout_2.addWidget(self.lblAvailTrades)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)


        self.general.addLayout(self.verticalLayout_3)


        self.verticalLayout_4.addLayout(self.general)

        self.Positions = QVBoxLayout()
        self.Positions.setObjectName(u"Positions")
        self.lblPositions = QLabel(self.layoutWidget)
        self.lblPositions.setObjectName(u"lblPositions")

        self.Positions.addWidget(self.lblPositions)

        self.hl = QHBoxLayout()
        self.hl.setObjectName(u"hl")
        self.scrollArea = QScrollArea(self.layoutWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1250, 72))
        self.gridLayout_2 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gp = QGridLayout()
        self.gp.setObjectName(u"gp")

        self.gridLayout_2.addLayout(self.gp, 0, 0, 1, 1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.hl.addWidget(self.scrollArea)


        self.Positions.addLayout(self.hl)


        self.verticalLayout_4.addLayout(self.Positions)

        self.splitter.addWidget(self.layoutWidget)
        self.layoutWidget2 = QWidget(self.splitter)
        self.layoutWidget2.setObjectName(u"layoutWidget2")
        self.candidates = QVBoxLayout(self.layoutWidget2)
        self.candidates.setObjectName(u"candidates")
        self.candidates.setContentsMargins(0, 0, 0, 0)
        self.lblCandidates = QLabel(self.layoutWidget2)
        self.lblCandidates.setObjectName(u"lblCandidates")

        self.candidates.addWidget(self.lblCandidates)

        self.tCandidates = QTableWidget(self.layoutWidget2)
        if (self.tCandidates.columnCount() < 9):
            self.tCandidates.setColumnCount(9)
        __qtablewidgetitem = QTableWidgetItem()
        self.tCandidates.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tCandidates.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tCandidates.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tCandidates.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tCandidates.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tCandidates.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.tCandidates.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.tCandidates.setHorizontalHeaderItem(7, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.tCandidates.setHorizontalHeaderItem(8, __qtablewidgetitem8)
        self.tCandidates.setObjectName(u"tCandidates")
        self.tCandidates.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.candidates.addWidget(self.tCandidates)

        self.splitter.addWidget(self.layoutWidget2)
        self.layoutWidget3 = QWidget(self.splitter)
        self.layoutWidget3.setObjectName(u"layoutWidget3")
        self.Orders = QVBoxLayout(self.layoutWidget3)
        self.Orders.setObjectName(u"Orders")
        self.Orders.setContentsMargins(0, 0, 0, 0)
        self.lblOrders = QLabel(self.layoutWidget3)
        self.lblOrders.setObjectName(u"lblOrders")

        self.Orders.addWidget(self.lblOrders)

        self.tOrders = QTableWidget(self.layoutWidget3)
        if (self.tOrders.columnCount() < 3):
            self.tOrders.setColumnCount(3)
        __qtablewidgetitem9 = QTableWidgetItem()
        self.tOrders.setHorizontalHeaderItem(0, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.tOrders.setHorizontalHeaderItem(1, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.tOrders.setHorizontalHeaderItem(2, __qtablewidgetitem11)
        self.tOrders.setObjectName(u"tOrders")

        self.Orders.addWidget(self.tOrders)

        self.splitter.addWidget(self.layoutWidget3)
        self.layoutWidget4 = QWidget(self.splitter)
        self.layoutWidget4.setObjectName(u"layoutWidget4")
        self.Console = QVBoxLayout(self.layoutWidget4)
        self.Console.setObjectName(u"Console")
        self.Console.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.layoutWidget4)
        self.label_2.setObjectName(u"label_2")

        self.Console.addWidget(self.label_2)

        self.consoleOut = QTextEdit(self.layoutWidget4)
        self.consoleOut.setObjectName(u"consoleOut")
        self.consoleOut.setReadOnly(True)

        self.Console.addWidget(self.consoleOut)

        self.splitter.addWidget(self.layoutWidget4)

        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Algo Traider", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Account:    ", None))
        self.lAcc.setText(QCoreApplication.translate("MainWindow", u"00000", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Liquidation Value: ", None))
        self.lMarketValue.setText(QCoreApplication.translate("MainWindow", u"000000", None))
#if QT_CONFIG(tooltip)
        self.label_7.setToolTip(QCoreApplication.translate("MainWindow", u"Available for use - required to get to maximum Loss", None))
#endif // QT_CONFIG(tooltip)
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"SMA(with buffer)", None))
        self.lSma.setText(QCoreApplication.translate("MainWindow", u"000000", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"All Positions", None))
        self.lPositionsTotalValue.setText(QCoreApplication.translate("MainWindow", u"000000", None))
        self.btnSettings.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"EST time :", None))
#if QT_CONFIG(tooltip)
        self.label_5.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Available hours: 04:00-20:00 EST</p><p>Actual trade:      09:30-16:00 EST</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"US Market:", None))
        self.lblTime.setText(QCoreApplication.translate("MainWindow", u"tbd", None))
        self.lblMarket.setText(QCoreApplication.translate("MainWindow", u"tbd", None))
        self.chbxProcess.setText(QCoreApplication.translate("MainWindow", u"Process Positions and Candidates", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Trades available: ", None))
        self.lblAvailTrades.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.lblPositions.setText(QCoreApplication.translate("MainWindow", u"Positions", None))
        self.lblCandidates.setText(QCoreApplication.translate("MainWindow", u"Candidates", None))
        ___qtablewidgetitem = self.tCandidates.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Stock", None));
        ___qtablewidgetitem1 = self.tCandidates.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Open", None));
        ___qtablewidgetitem2 = self.tCandidates.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Close", None));
        ___qtablewidgetitem3 = self.tCandidates.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Bid", None));
        ___qtablewidgetitem4 = self.tCandidates.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"Ask", None));
        ___qtablewidgetitem5 = self.tCandidates.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"Target price", None));
        ___qtablewidgetitem6 = self.tCandidates.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"Average drop", None));
        ___qtablewidgetitem7 = self.tCandidates.horizontalHeaderItem(7)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"Rank", None));
        ___qtablewidgetitem8 = self.tCandidates.horizontalHeaderItem(8)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"Last Update", None));
        self.lblOrders.setText(QCoreApplication.translate("MainWindow", u"Orders", None))
        ___qtablewidgetitem9 = self.tOrders.horizontalHeaderItem(0)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"Stock", None));
        ___qtablewidgetitem10 = self.tOrders.horizontalHeaderItem(1)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"Action", None));
        ___qtablewidgetitem11 = self.tOrders.horizontalHeaderItem(2)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"Type", None));
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Console", None))
    # retranslateUi

