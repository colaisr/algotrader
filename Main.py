import configparser
import json
import subprocess
import sys
import traceback
from datetime import datetime
from sys import platform
# checking branch

from PySide2 import QtGui
from PySide2.QtCore import QRunnable, Slot, QThreadPool, Signal, QObject, QTimer, QTime
from PySide2.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QMessageBox
from pytz import timezone

from AlgotraderServerConnection import report_snapshot_to_server, \
    get_user_settings_from_server, get_user_candidates_from_server, \
    get_market_data_from_server, get_command_from_server
from Logic.IBKRWorker import IBKRWorker
# The bid price refers to the highest price a buyer will pay for a security.
# The ask price refers to the lowest price a seller will accept for a security.
# UI Imports
from UI.MainWindow import Ui_MainWindow

def restart_tws_and_trader():
    import platform
    if platform.system()=='Windows':
        import sys
        print("argv was", sys.argv)
        print("sys.executable was", sys.executable)
        print("restart now")

        import os
        subprocess.call('restartTws.bat')
        os.execv(sys.executable, ['python'] + sys.argv)
    elif platform.system()=='Linux':
        #not implemented
        pass
    elif platform.system()=='Darwin':
        #not implemented
        pass


class SettingsCandidate:
    def __init__(self):
        self.ticker = ''
        self.reason = ''


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    """
    finished = Signal()  # QtCore.Signal
    error = Signal(tuple)
    result = Signal(object)  # returned by end of function
    status = Signal(object)  # to update a status bar
    notification = Signal(object)  # to update a Console
    progress = Signal(int)  # to use for progress if needed


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['notification_callback'] = self.signals.notification
        self.kwargs['status_callback'] = self.signals.status

    @Slot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class TraderSettings():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.FILESERVERURL = self.config['Server']['serverurl']
        self.FILESERVERUSER = self.config['Server']['serveruser']
        retrieved = get_user_settings_from_server(self.FILESERVERURL, self.FILESERVERUSER)

        self.read_config(retrieved)

    def read_config(self, retrieved):
        self.PORT = retrieved['connection_port']
        self.ACCOUNT = retrieved['connection_account_name']
        self.INTERVALUI = retrieved['station_interval_ui_sec']
        self.INTERVALWORKER = retrieved['station_interval_worker_sec']
        # alg
        self.PROFIT = retrieved['algo_take_profit']
        self.LOSS = retrieved['algo_max_loss']
        self.TRAIL = retrieved['algo_trailing_percent']
        self.BULCKAMOUNT = retrieved['algo_bulk_amount_usd']
        self.USEMARGIN = retrieved['algo_allow_margin']
        self.SERVERURL = self.FILESERVERURL
        self.SERVERUSER = self.FILESERVERUSER
        self.INTERVALSERVER = retrieved['server_report_interval_sec']
        self.ALLOWBUY = retrieved['algo_allow_buy']


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        # mandatory
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.trading_session_state = "TBD"
        self.trading_time_zone = timezone('US/Eastern')
        self.setupUi(self)
        self.setWindowTitle("Algo Traider v 4.19")

        self.settings = None
        self.uiTimer = QTimer()
        self.workerTimer = QTimer()
        self.server_timer = QTimer()
        self.stocks_data_from_server =None

    def showEvent(self, event):
        super().showEvent(event)
        self.update_console('Connecting to server - to get settings.')
        self.settings=TraderSettings()
        self.update_console('Settings received.')
        StyleSheet = '''
        #lcdPNLgreen {
            border: 3px solid green;
        }
        #lcdPNLred {
            border: 3px solid red;
        }
        '''
        self.setStyleSheet(StyleSheet)

        self.threadpool = QThreadPool()
        # setting all timers

        # self.uiTimer.timeout.connect(self.update_ui)
        # self.workerTimer.timeout.connect(self.run_worker)
        #
        self.get_command_from_server()
        self.server_timer.timeout.connect(self.get_command_from_server)
        self.server_timer.start(int(self.settings.INTERVALSERVER) * 1000)
        #
        # self.statusbar.showMessage("Ready")
        #
        # stock_names = [o.ticker for o in self.settings.CANDIDATES]
        # self.stocks_data_from_server = get_market_data_from_server(self.settings, stock_names)
        # self.ibkrworker.stocks_data_from_server = get_market_data_from_server(self.settings, stock_names)
        # self.update_console("Market data for " + str(len(stock_names)) + " Candidates received from Server")
        # self.ibkrworker = IBKRWorker(self.settings)
        #
        # self.connect_to_ibkr()

    def get_command_from_server(self):
        self.update_console('Getting server command')
        worker = Worker(get_command_from_server, self.settings)
        worker.signals.result.connect(self.process_server_command_response)
        self.threadpool.start(worker)

    def connect_and_proceed(self):
        self.process_ibkr_cycle()

    def process_ibkr_cycle(self):
        self.ibkrworker = IBKRWorker(self.settings)
        self.ibkrworker.stocks_data_from_server = self.stocks_data_from_server
        connector = Worker(self.ibkrworker.run_full_cycle)
        connector.signals.result.connect(self.ibkr_cycle_finished)
        connector.signals.status.connect(self.update_status)
        connector.signals.notification.connect(self.update_console)
        # Execute
        self.threadpool.start(connector)

    def ibkr_cycle_finished(self,r):

        if r:
            self.update_ui()
            self.report_to_server()
        else:
            pass



    def connect_to_ibkr(self):

        # result = report_login_to_server(self.settings)
        # self.update_console(result)
        self.ibkrworker=IBKRWorker(self.settings)
        self.ibkrworker.stocks_data_from_server=self.stocks_data_from_server
        connector = Worker(self.ibkrworker.prepare_and_connect)
        connector.signals.result.connect(self.connection_done)
        connector.signals.status.connect(self.update_status)
        connector.signals.notification.connect(self.update_console)
        # Execute
        self.threadpool.start(connector)

    def run_worker(self):
        """
Executed the Worker in separate thread
        """

        # exec(open('restarter.py').read())
        # sys.exit()
        self.update_session_state()
        # self.update_console("Starting Worker- UI Paused")
        # self.uiTimer.stop()  # to not cause an errors when lists will be resetted
        worker = Worker(
            self.ibkrworker.process_positions_candidates)  # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.update_ui)
        worker.signals.status.connect(self.update_status)
        worker.signals.notification.connect(self.update_console)
        # Execute
        self.threadpool.start(worker)

    def connection_done(self):
        # add processing
        self.update_ui()
        self.run_worker()
        # self.workerTimer.start(int(self.settings.INTERVALWORKER) * 1000)

        # # report market data to server
        # if self.settings.USESERVER:
        #     print("Reporting market data to the server...")
        #     result = report_market_data_to_server(self.settings, self.ibkrworker.app.candidatesLive)
        #     self.update_console(result)

    def report_to_server(self):
        net_liquidation = self.ibkrworker.app.netLiquidation
        if hasattr(self.ibkrworker.app, 'smaWithSafety'):
            remaining_sma_with_safety = self.ibkrworker.app.smaWithSafety
        else:
            remaining_sma_with_safety = self.ibkrworker.app.sMa
        excess_liquidity = self.ibkrworker.app.excessLiquidity
        remaining_trades = self.ibkrworker.app.tradesRemaining
        all_positions_value = 0
        open_positions = self.ibkrworker.app.openPositions
        open_orders = self.ibkrworker.app.openOrders
        candidates_live=self.ibkrworker.app.candidatesLive
        dailyPnl = self.ibkrworker.app.dailyPnl
        tradinng_session_state = self.trading_session_state
        worker_last_execution = self.ibkrworker.last_worker_execution_time
        data_for_report = [self.settings,
                           net_liquidation,
                           remaining_sma_with_safety,
                           remaining_trades,
                           all_positions_value,
                           open_positions,
                           open_orders,
                           candidates_live,
                           dailyPnl,
                           worker_last_execution,
                           datetime.now(self.trading_time_zone),
                           self.trading_session_state,
                           excess_liquidity]

        worker = Worker(
            report_snapshot_to_server, self.settings, data_for_report)

        worker.signals.result.connect(self.process_server_report_response)
        # Execute
        self.threadpool.start(worker)

    def process_server_command_response(self, r):
        response=json.loads(r)
        self.stocks_data_from_server=response['candidates']
        command=response['command']
        self.update_console('processing command : '+command)
        if command=='restart_worker':
            self.update_console('Restart command received- doing restart for Algotrader and TWS')
            restart_tws_and_trader()
        else:
            self.connect_and_proceed()

    def process_server_report_response(self, r):
        self.update_console(r)

    def update_ui(self):
        """
Updates UI after connection/worker execution
        """
        # main data
        self.lAcc.setText(self.settings.ACCOUNT)
        # self.lExcessLiquidity.setText(str(self.ibkrworker.app.excessLiquidity))
        # self.lSma.setText(str(self.ibkrworker.app.sMa))
        if hasattr(self.ibkrworker.app, 'smaWithSafety'):
            self.lSma.setText(str(round(self.ibkrworker.app.smaWithSafety, 1)))
        else:
            self.lSma.setText(str(round(self.ibkrworker.app.sMa, 1)))
        self.lMarketValue.setText(str(self.ibkrworker.app.netLiquidation))
        self.lblAvailTrades.setText(str(self.ibkrworker.app.tradesRemaining))
        self.lcdPNL.display(self.ibkrworker.app.dailyPnl)
        if self.ibkrworker.app.dailyPnl > 0:
            palette = self.lcdPNL.palette()
            palette.setColor(palette.WindowText, QtGui.QColor(51, 153, 51))
            self.lcdPNL.setPalette(palette)
        elif self.ibkrworker.app.dailyPnl < 0:
            palette = self.lcdPNL.palette()
            palette.setColor(palette.WindowText, QtGui.QColor(255, 0, 0))
            self.lcdPNL.setPalette(palette)

        total_positions_value = 0
        for p in self.ibkrworker.app.openPositions.values():
            if hasattr(p, 'Value'):
                total_positions_value += p["Value"]
        self.lPositionsTotalValue.setText(str(round(total_positions_value, 1)))

        self.update_open_positions()
        self.update_live_candidates()
        self.update_open_orders()

        self.update_session_state()

        if not self.uiTimer.isActive():
            self.update_console("UI resumed.")
        self.uiTimer.start(int(self.settings.INTERVALUI) * 1000)  # reset the ui timer

    def update_session_state(self):
        fmt = '%Y-%m-%d %H:%M:%S'
        self.est_dateTime = datetime.now(self.trading_time_zone)
        self.est_current_time = QTime(self.est_dateTime.hour, self.est_dateTime.minute, self.est_dateTime.second)
        self.lblTime.setText(self.est_current_time.toString())
        dStart = QTime(4, 00)
        dEnd = QTime(20, 00)
        tStart = QTime(9, 30)
        tEnd = QTime(16, 0)
        self.ibkrworker.check_if_holiday()
        if not self.ibkrworker.trading_session_holiday:
            if self.est_current_time > dStart and self.est_current_time <= tStart:
                self.ibkrworker.trading_session_state = "Pre Market"
                self.lblMarket.setText("Pre Market")
            elif self.est_current_time > tStart and self.est_current_time <= tEnd:
                self.ibkrworker.trading_session_state = "Open"
                self.lblMarket.setText("Open")
            elif self.est_current_time > tEnd and self.est_current_time <= dEnd:
                self.ibkrworker.trading_session_state = "After Market"
                self.lblMarket.setText("After Market")
            else:
                self.ibkrworker.trading_session_state = "Closed"
                self.lblMarket.setText("Closed")
        else:
            self.ibkrworker.trading_session_state = "Holiday"
            self.lblMarket.setText("Holiday")
        self.trading_session_state = self.ibkrworker.trading_session_state

    def update_status(self, s):
        """
Updates StatusBar on event of Status
        :param s:
        """
        self.statusbar.showMessage(s)

    def update_console(self, n):
        """
Adds Message to console- upon event
        :param n:
        """
        self.consoleOut.append(n)

    def update_live_candidates(self):
        """
Updates Candidates table
        """

        liveCandidates = self.ibkrworker.app.candidatesLive
        try:
            line = 0
            self.tCandidates.setRowCount(len(liveCandidates))
            for k, v in liveCandidates.items():
                self.tCandidates.setItem(line, 0, QTableWidgetItem(v['Stock']))
                self.tCandidates.setItem(line, 1, QTableWidgetItem(str(v['Open'])))
                self.tCandidates.setItem(line, 2, QTableWidgetItem(str(v['Close'])))
                self.tCandidates.setItem(line, 3, QTableWidgetItem(str(v['Bid'])))
                self.tCandidates.setItem(line, 4, QTableWidgetItem(str(v['Ask'])))
                if v['Ask'] < v['target_price'] and v['Ask'] != -1:
                    self.tCandidates.item(line, 4).setBackground(QtGui.QColor(0, 255, 0))
                if v['target_price'] is float:
                    self.tCandidates.setItem(line, 5, QTableWidgetItem(str(round(v['target_price'], 2))))
                else:
                    self.tCandidates.setItem(line, 5, QTableWidgetItem(str(v['target_price'])))
                self.tCandidates.setItem(line, 6, QTableWidgetItem(str(round(v['averagePriceDropP'], 2))))
                if v['tipranksRank'] == '':
                    v['tipranksRank'] = 0
                self.tCandidates.setItem(line, 7, QTableWidgetItem(str(v['tipranksRank'])))
                if int(v['tipranksRank']) > 7:
                    self.tCandidates.item(line, 7).setBackground(QtGui.QColor(0, 255, 0))
                self.tCandidates.setItem(line, 8, QTableWidgetItem(str(v['fmp_rating'])))
                self.tCandidates.setItem(line, 9, QTableWidgetItem(str(v['LastUpdate'])))

                line += 1
        except Exception as e:
            if hasattr(e, 'message'):
                self.update_console("Error in updating Candidates: " + str(e.message))
            else:
                self.update_console("Error in updating Candidates: " + str(e))

    def update_open_positions(self):
        """
Updates Positions grid
        """
        open_positions = self.ibkrworker.app.openPositions

        try:
            line = 0
            self.tPositions.setRowCount(len(open_positions))
            for k, v in open_positions.items():
                self.tPositions.setItem(line, 0, QTableWidgetItem(k))
                self.tPositions.setItem(line, 1, QTableWidgetItem(str(round(v['DailyPnL'], 2))))
                if v['DailyPnL'] >0:
                    self.tPositions.item(line, 1).setBackground(QtGui.QColor(194, 240, 194))
                else:
                    self.tPositions.item(line, 1).setBackground(QtGui.QColor(255, 173, 153))
                self.tPositions.setItem(line, 2, QTableWidgetItem(str(round(v['UnrealizedPnL'], 2))))
                if v['UnrealizedPnL'] >0:
                    self.tPositions.item(line, 2).setBackground(QtGui.QColor(40, 164, 40))
                else:
                    self.tPositions.item(line, 2).setBackground(QtGui.QColor(255, 51, 0))
                self.tPositions.setItem(line, 3, QTableWidgetItem(str(round(v['Value'], 2))))
                self.tPositions.setItem(line, 4, QTableWidgetItem(str(v['stocks'])))
                self.tPositions.setItem(line, 5, QTableWidgetItem(str(v['LastUpdate'])))
                line += 1
        except Exception as e:
            if hasattr(e, 'message'):
                self.update_console("Error in refreshing Positions: " + str(e.message))
            else:
                self.update_console("Error in refreshing Positions: " + str(e))

    def update_open_orders(self):
        """
Updates Positions table
        """
        openOrders = self.ibkrworker.app.openOrders
        try:
            line = 0
            self.tOrders.setRowCount(len(openOrders))
            for k, v in openOrders.items():
                self.tOrders.setItem(line, 0, QTableWidgetItem(k))
                self.tOrders.setItem(line, 1, QTableWidgetItem(v['Action']))
                self.tOrders.setItem(line, 2, QTableWidgetItem(v['Type']))
                line += 1
        except Exception as e:
            if hasattr(e, 'message'):
                self.update_console("Error in Updating open Orders : " + str(e.message))
            else:
                self.update_console("Error in Updating open Orders : " + str(e))


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
