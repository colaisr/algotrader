
from datetime import time
import traceback, sys

from PySide2.QtCore import QRunnable, Slot, QThreadPool, Signal, QObject
from PySide2.QtGui import QColor
from PySide2.QtUiTools import loadUiType
from PySide2.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from Logic.IBKRWorker import IBKRWorker

qt_creator_file = "UI/MainWindow.ui"
Ui_MainWindow, QtBaseClass = loadUiType(qt_creator_file)


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    '''
    finished = Signal()  # QtCore.Signal
    error = Signal(tuple)
    result = Signal(object)
    status = Signal(object)

class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()  # QtCore.Slot
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(
                *self.args, **self.kwargs
            )
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.ibkrworker = IBKRWorker()
        self.threadpool = QThreadPool()

        self.btnConnect.pressed.connect(self.connect_to_ibkr)
        self.btnStart.pressed.connect(self.StartWorker)

    def connect_to_ibkr(self):
        self.btnConnect.setEnabled(False)
        # Connect and load
        # Pass the function to execute
        worker = Worker(self.ibkrworker.connectToIBKR)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.update_ui)
        worker.signals.finished.connect(self.thread_complete)
        # Execute
        self.threadpool.start(worker)


    def StartWorker(self):
        # Pass the function to execute
        worker = Worker(self.ibkrworker.startLooping)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.update_ui)
        worker.signals.finished.connect(self.thread_complete)
        # Execute
        self.threadpool.start(worker)

    def update_ui(self, s):
        self.lLiq.setText(self.ibkrworker.app.excessLiquidity)
        self.lAcc.setText(self.ibkrworker.ACCOUNT)
        openPostions=self.ibkrworker.app.openPositions
        line=0
        self.tPositions.setRowCount(len(openPostions))
        for k,v in openPostions.items():
            self.tPositions.setItem(line, 0, QTableWidgetItem(k))
            self.tPositions.setItem(line, 1, QTableWidgetItem(str(int(v['stocks']))))
            self.tPositions.setItem(line, 2, QTableWidgetItem(str(round(v['cost'],2))))
            self.tPositions.setItem(line, 3, QTableWidgetItem(str(round(v['Value'],2))))
            self.tPositions.setItem(line, 4, QTableWidgetItem(str(round(v['UnrealizedPnL'],2))))

            profit=v['UnrealizedPnL']/v['Value']*100
            self.tPositions.setItem(line, 5, QTableWidgetItem(str(round(profit,2))))

            if v['UnrealizedPnL']>0:
                self.tPositions.item(line, 4).setBackgroundColor(QColor(51, 204, 51))
                self.tPositions.item(line, 5).setBackgroundColor(QColor(51, 204, 51))
            else:
                self.tPositions.item(line, 4).setBackgroundColor(QColor(255, 51, 0))
                self.tPositions.item(line, 5).setBackgroundColor(QColor(255, 51, 0))
            line+=1






    def thread_complete(self):
        print("THREAD COMPLETE!")





app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())