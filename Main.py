import sys
from PySide2.QtUiTools import loadUiType
from PySide2.QtWidgets import QMainWindow, QApplication
from Logic.IBKRWorker import IBKRWorker

qt_creator_file = "UI/MainWindow.ui"
Ui_MainWindow, QtBaseClass = loadUiType(qt_creator_file)



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.worker = IBKRWorker()





app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())