import sys

from PySide2.QtWidgets import QApplication, QWidget, QGridLayout, QLineEdit, QLabel, QMainWindow


class EchoText(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.textbox = QLineEdit()
        self.echo_label = QLabel('')

        self.textbox.textChanged.connect(self.textbox_text_changed)

        self.layout.addWidget(self.textbox, 0, 0)
        self.layout.addWidget(self.echo_label, 1, 0)

    def textbox_text_changed(self):
        self.echo_label.setText(self.textbox.text())


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_gui()

    def init_gui(self):
        self.window = QWidget()
        self.layout = QGridLayout()
        self.setCentralWidget(self.window)
        self.window.setLayout(self.layout)

        self.echotext_widget = EchoText()

        for p in range(0,5):

            self.layout.addWidget(self.echotext_widget)




if __name__ == '__main__':
    app = QApplication([])

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
