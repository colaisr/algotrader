from UI.MainWindow import Ui_MainWindow
import sys
from PySide2.QtWidgets import QApplication, QMainWindow

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())