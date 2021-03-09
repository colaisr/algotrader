import ast
import configparser
import copy
import json
import sys
import os
import traceback
from datetime import datetime, time, date
from sys import platform

import pyqtgraph as pg
import requests
from PySide2 import QtGui
from PySide2.QtCore import QRunnable, Slot, QThreadPool, Signal, QObject, QTimer, QTime, Qt
from PySide2.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QWidget, QMessageBox, QListWidgetItem, \
    QDialog
from pytz import timezone

from AlgotraderServerConnection import report_snapshot_to_server, report_login_to_server, \
    report_market_data_to_server, get_user_settings_from_server, get_user_candidates_from_server, \
    get_market_data_from_server
from Logic.IBKRWorker import IBKRWorker
# The bid price refers to the highest price a buyer will pay for a security.
# The ask price refers to the lowest price a seller will accept for a security.
# from Research.tipRanksScrapperRequestsHtmlThreaded import get_tiprank_ratings_to_Stocks
# UI Imports
from Research.UpdateCandidates import get_yahoo_stats_for_candidate
from Research.tipRanksScrapperSelenium import open_tip_ranks_page, get_tiprank_rating_for_ticker
from UI.MainWindow import Ui_MainWindow
from UI.NewStockWindow import Ui_newStockDlg
from UI.SettingsWindow import Ui_setWin
from UI.pos import Ui_position_canvas

LOGFILE = "LOG/log.txt"

global window
global settings


def restart():
    import sys
    print("argv was", sys.argv)
    print("sys.executable was", sys.executable)
    print("restart now")

    import os
    # os.execv(sys.executable, ['python'] + sys.argv)
    os.execv("Play.bat",[' '])


class SettingsCandidate:
    def __init__(self):
        self.ticker = ''
        self.reason = ''


class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [datetime.fromtimestamp(value).strftime("%H:%M") for value in values]


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
        if platform == "linux" or platform == "linux2":
            self.PATHTOWEBDRIVER = retrieved['station_linux_path_to_webdriver']
        elif platform == "darwin":  # mac os
            self.PATHTOWEBDRIVER = retrieved['station_mac_path_to_webdriver']
        elif platform == "win32":
            self.PATHTOWEBDRIVER = retrieved['station_win_path_to_webdriver']
        # alg
        self.PROFIT = retrieved['algo_take_profit']
        self.LOSS = retrieved['algo_max_loss']
        self.TRAIL = retrieved['algo_trailing_percent']
        self.BULCKAMOUNT = retrieved['algo_bulk_amount_usd']
        self.TECHFROMHOUR = retrieved['connection_break_from_hour']
        self.TECHFROMMIN = retrieved['connection_break_from_min']
        self.TECHTOHOUR = retrieved['connection_break_to_hour']
        self.TECHTOMIN = retrieved['connection_break_to_min']
        self.UIDEBUG = retrieved['station_debug_ui']
        self.AUTOSTART = retrieved['station_autostart_worker']
        self.USESERVER = True
        self.USEMARGIN=retrieved['algo_allow_margin']
        self.SERVERURL = self.FILESERVERURL
        self.SERVERUSER = self.FILESERVERUSER
        self.INTERVALSERVER = retrieved['server_report_interval_sec']
        self.USESYSTEMCANDIDATES = retrieved['server_use_system_candidates']
        self.ALLOWBUY=retrieved['algo_allow_buy']
        self.CANDIDATES = []
        dictionaries = get_user_candidates_from_server(self.SERVERURL, self.SERVERUSER, self.USESYSTEMCANDIDATES)
        for c in dictionaries:
            ticker = c['ticker']
            reason = c['description']
            ca = SettingsCandidate()
            ca.ticker = ticker
            ca.reason = reason
            self.CANDIDATES.append(ca)

    def write_config(self):
        self.config['Connection']['port'] = self.PORT
        self.config['Account']['acc'] = self.ACCOUNT
        self.config['Connection']['INTERVALUI'] = str(self.INTERVALUI)
        self.config['Connection']['INTERVALWORKER'] = str(self.INTERVALWORKER)
        if platform == "linux" or platform == "linux2":
            self.config['Connection']['linuxpathtowebdriver'] = self.PATHTOWEBDRIVER
        elif platform == "darwin":  # mac os
            self.config['Connection']['macPathToWebdriver'] = self.PATHTOWEBDRIVER
        elif platform == "win32":
            self.config['Connection']['winPathToWebdriver'] = self.PATHTOWEBDRIVER
        # alg
        self.config['Algo']['gainP'] = str(self.PROFIT)
        self.config['Algo']['lossP'] = str(self.LOSS)
        self.config['Algo']['trailstepP'] = str(self.TRAIL)
        self.config['Algo']['bulkAmountUSD'] = str(self.BULCKAMOUNT)
        self.config['Algo']['TrandingStocks'] = str(self.TRANDINGSTOCKS)
        json_string = json.dumps([ob.__dict__ for ob in self.CANDIDATES])
        self.config['Algo']['Candidates'] = json_string
        self.config['Connection']['techfromHour'] = str(self.TECHFROMHOUR)
        self.config['Connection']['techfromMin'] = str(self.TECHFROMMIN)
        self.config['Connection']['techtoHour'] = str(self.TECHTOHOUR)
        self.config['Connection']['techtoMin'] = str(self.TECHTOMIN)
        self.config['Soft']['uidebug'] = str(self.UIDEBUG)
        self.config['Soft']['autostart'] = str(self.AUTOSTART)
        self.config['Server']['useserver'] = str(self.USESERVER)
        self.config['Server']['serverurl'] = str(self.SERVERURL)
        self.config['Server']['serveruser'] = str(self.SERVERUSER)
        self.config['Server']['INTERVALSERVER'] = str(self.INTERVALSERVER)

        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, settings):
        # mandatory
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.trading_session_state = "TBD"
        self.est = timezone('US/Eastern')
        self.settingsWindow = SettingsWindow()
        self.setupUi(self)
        self.settings = settings
        self.ibkrworker = IBKRWorker(self.settings)
        self.threadpool = QThreadPool()
        self.setWindowTitle("Algo Traider v 2.0")

        sys.stderr = open('LOG/errorLog.txt', 'w')

        self.create_open_positions_grid()

        # setting a timer for Worker

        self.uiTimer = QTimer()
        self.uiTimer.timeout.connect(self.update_ui)

        self.workerTimer = QTimer()
        self.workerTimer.timeout.connect(self.run_worker)

        self.server_timer = QTimer()
        self.server_timer.timeout.connect(self.report_to_server)
        self.server_timer.start(int(self.settings.INTERVALSERVER) * 1000)

        # connecting a buttons
        self.chbxProcess.stateChanged.connect(self.process_checked)
        self.btnSettings.pressed.connect(self.show_settings)

        self.statusbar.showMessage("Ready")

        stock_names = [o.ticker for o in self.settings.CANDIDATES]
        self.ibkrworker.stocks_data_from_server = get_market_data_from_server(self.settings, stock_names)
        self.update_console("Market data for " + str(len(stock_names)) + " Candidates received from Server")
        self.start_updating_candidates_and_connect()

        StyleSheet = '''
        #lcdPNLgreen {
            border: 3px solid green;
        }
        #lcdPNLred {
            border: 3px solid red;
        }
        '''
        self.setStyleSheet(StyleSheet)

    def update_candidates_info(self, status_callback, notification_callback):
        today_dt = date.today()
        for c in self.ibkrworker.stocks_data_from_server:
            updated_dt = c['tiprank_updated'].date()
            if today_dt != updated_dt:
                # yahoo
                notification_callback.emit('Update for ' + c['ticker'] + ' needed:')
                notification_callback.emit('Checking for Yahoo statisticks...')
                drop, change = get_yahoo_stats_for_candidate(c['ticker'], notification_callback)
                c['yahoo_avdropP'] = drop
                c['yahoo_avspreadP'] = change
                notification_callback.emit(
                    'Got ' + str(drop) + ' average daily drop and ' + str(change) + ' average daily change.')
                # tipranks
                notification_callback.emit('Checking for Tiprank...')
                rank = get_tiprank_rating_for_ticker(c['ticker'], self.settings.PATHTOWEBDRIVER)
                notification_callback.emit('Got rank of :' + str(rank))
                c['tipranks'] = rank
                c['tiprank_updated']=today_dt
            else:
                notification_callback.emit('Data for ' + c['ticker'] + ' is up to the date,no update needed')
        report_market_data_to_server(self.settings,self.ibkrworker.stocks_data_from_server)

        return 'done'

    def start_updating_candidates_and_connect(self):

        cand = Worker(self.update_candidates_info)
        cand.signals.result.connect(self.connect_to_ibkr)
        # connector.signals.status.connect(self.update_status)
        cand.signals.notification.connect(self.update_console)
        # Execute
        self.threadpool.start(cand)

    def connect_to_ibkr(self):
        """
Starts the connection to the IBKR terminal in separate thread
        """

        self.update_console("Reporting connection to the server...")
        print("Reporting connection to the server...")
        result = report_login_to_server(self.settings)
        self.update_console(result)
        connector = Worker(self.ibkrworker.prepare_and_connect)
        connector.signals.result.connect(self.connection_done)
        connector.signals.status.connect(self.update_status)
        connector.signals.notification.connect(self.update_console)
        # Execute
        self.threadpool.start(connector)

    def process_checked(self):
        """
Starts the Timer with interval from Config file
        """
        if self.chbxProcess.isChecked():
            self.run_worker()
            self.workerTimer.start(int(self.settings.INTERVALWORKER) * 1000)
        else:
            self.workerTimer.stop()

    # noinspection PyUnresolvedReferences
    def run_worker(self):
        """
Executed the Worker in separate thread
        """

        # exec(open('restarter.py').read())
        # sys.exit()
        self.update_session_state()
        currentTime = QTime().currentTime()
        fromTime = QTime(int(self.settings.TECHFROMHOUR), int(self.settings.TECHFROMMIN))
        toTime = QTime(int(self.settings.TECHTOHOUR), int(self.settings.TECHTOMIN))
        sessionState = self.lblMarket.text()

        if fromTime < currentTime < toTime:
            print("Worker skept-Technical break : ", fromTime.toString("hh:mm"), " to ", toTime.toString("hh:mm"))
            self.update_console("Technical break untill " + toTime.toString("hh:mm"))

        else:
            self.update_console("Starting Worker- UI Paused")
            self.uiTimer.stop()  # to not cause an errors when lists will be resetted
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
        if self.settings.AUTOSTART:
            self.chbxProcess.setChecked(True)

        # # report market data to server
        # if self.settings.USESERVER:
        #     print("Reporting market data to the server...")
        #     result = report_market_data_to_server(self.settings, self.ibkrworker.app.candidatesLive)
        #     self.update_console(result)

    def report_to_server(self):
        """
       reports to the server
        """

        if self.settings.USESERVER:
            net_liquidation = self.ibkrworker.app.netLiquidation
            if hasattr(self.ibkrworker.app, 'smaWithSafety'):
                remaining_sma_with_safety = self.ibkrworker.app.smaWithSafety
            else:
                remaining_sma_with_safety = self.ibkrworker.app.sMa
            excess_liquidity=self.ibkrworker.app.excessLiquidity
            remaining_trades = self.ibkrworker.app.tradesRemaining
            all_positions_value = 0
            open_positions = self.ibkrworker.app.openPositions
            open_orders = self.ibkrworker.app.openOrders
            dailyPnl = self.ibkrworker.app.dailyPnl
            tradinng_session_state = self.trading_session_state
            data_for_report = [self.settings,
                               net_liquidation,
                               remaining_sma_with_safety,
                               remaining_trades,
                               all_positions_value,
                               open_positions,
                               open_orders,
                               dailyPnl,
                               self.ibkrworker.last_worker_execution_time,
                               datetime.now(self.est),
                               self.trading_session_state,
                               excess_liquidity]

            worker = Worker(
                report_snapshot_to_server, self.settings, data_for_report)

            worker.signals.result.connect(self.process_server_response)
            # Execute
            self.threadpool.start(worker)

    def process_server_response(self, r):
        # trying to restart
        if '$restart$' in r:
            restart()
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

        # everything disabled for safety - is now enabled
        self.chbxProcess.setEnabled(True)
        self.btnSettings.setEnabled(True)

        self.update_session_state()

        if not self.uiTimer.isActive():
            self.update_console("UI resumed.")
        self.uiTimer.start(int(self.settings.INTERVALUI) * 1000)  # reset the ui timer

    def update_session_state(self):
        fmt = '%Y-%m-%d %H:%M:%S'
        self.est_dateTime = datetime.now(self.est)
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

    def progress_fn(self, n):
        msgBox = QMessageBox()
        msgBox.setText(str(n))
        retval = msgBox.exec_()

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
        self.log_message(n)

    def log_message(self, message):
        """
Adds message to the standard log
        :param message:
        """
        with open(LOGFILE, "a") as f:
            currentDt = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            message = "\n" + currentDt + '---' + message
            f.write(message)

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
                self.tCandidates.setItem(line, 8, QTableWidgetItem(str(v['LastUpdate'])))

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
        allKeys = [*open_positions]
        lastUpdatedWidget = 0
        try:
            for i in range(len(open_positions)):  # Update positions Panels

                widget = self.gp.itemAt(i).widget()
                key = allKeys[i]
                values = open_positions[key]
                if 'stocks' in values.keys():
                    if values['stocks'] != 0:
                        candidate = next((x for x in self.settings.CANDIDATES if x.ticker == key), None)
                        reason_of_candidate = "Bought manually"
                        if candidate is not None:
                            reason_of_candidate = candidate.reason
                        widget.update_view(key, values, reason_of_candidate)
                        widget.show()
                        lastUpdatedWidget = i
                    else:
                        widgetToRemove = self.gp.itemAt(i).widget()
                        widgetToRemove.hide()
                else:
                    print("value not yet received")

            for i in range(self.gp.count()):  # Hide the rest of the panels
                if i > lastUpdatedWidget:
                    widgetToRemove = self.gp.itemAt(i).widget()
                    widgetToRemove.hide()
        except Exception as e:
            if hasattr(e, 'message'):
                self.update_console("Error in refreshing Positions: " + str(e.message))
            else:
                self.update_console("Error in refreshing Positions: " + str(e))

    def create_open_positions_grid(self):
        """
Creates Open positions grid with 99 Positions widgets
        """

        counter = 0
        col = 0
        row = 0

        for i in range(0, 99):
            if counter % 3 == 0:
                col = 0
                row += 1
            self.gp.addWidget(PositionPanel(), row, col)
            counter += 1
            col += 1

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

    def thread_complete(self):
        """
After threaded task finished
        """
        print("TREAD COMPLETE (good or bad)!")

    def show_settings(self):

        # self.settingsWindow = SettingsWindowO(self.settings)
        # self.settingsWindow.show()  # Показываем окно
        # # maybe not needed
        # self.settingsWindow.changedSettings = False
        self.settingsWindow.existingSettings = copy.deepcopy(self.settings)
        self.settingsWindow.changedSettings = False
        self.settingsWindow.ibkrClient = self.ibkrworker
        if self.settingsWindow.exec_():
            self.settings = self.settingsWindow.existingSettings
            self.settings.write_config()
            self.restart_all()
        else:
            print("Settings window Canceled")
        self.settingsWindow = SettingsWindow()

    def restart_all(self):
        """
Restarts everything after Save
        """
        self.threadpool.waitForDone()
        self.update_console("UI paused- for restart")
        self.uiTimer.stop()

        self.workerTimer.stop()
        self.update_console("Configuration changed - restarting everything")
        self.chbxProcess.setEnabled(False)
        self.chbxProcess.setChecked(False)
        self.btnSettings.setEnabled(False)
        self.ibkrworker.app.disconnect()
        while self.ibkrworker.app.isConnected():
            print("waiting for disconnect")
            time.sleep(1)

        self.ibkrworker = None
        self.ibkrworker = IBKRWorker(self.settings)
        self.connect_to_ibkr()

        i = 4


class PositionPanel(QWidget):

    def __init__(self):
        super(PositionPanel, self).__init__()
        self.ui = Ui_position_canvas()
        self.ui.setupUi(self)

        # # to be able to address it  on refresh
        # date_axis = TimeAxisItem(orientation='bottom')
        # self.graphWidget = pg.PlotWidget(axisItems={'bottom': date_axis})
        # self.ui.gg.addWidget(self.graphWidget)

    def update_view(self, stock, values, description):
        # Data preparation
        try:
            stock = stock
            number_of_stocks = values['stocks']
            bulk_value = 0
            profit = 0
            bid_price = str(round(values['cost'], 2))
            if 'Value' in values.keys():
                bulk_value = str(round(values['Value'], 2))
            if 'UnrealizedPnL' in values.keys():
                unrealized_pnl = str(round(values['UnrealizedPnL'], 2))
                profit = values['UnrealizedPnL'] / values['Value'] * 100
            if 'LastUpdate' in values.keys():
                last_updatestr = (values['LastUpdate'])
            # if 'HistoricalData' in values.keys():
            #     print("Updating Graph for " + stock + " using " + str(len(values['HistoricalData'])) + " points")
            #     if len(values['HistoricalData']) > 0:
            #         hist_data = values['HistoricalData']
            #         dates = []
            #         counter = []
            #         values = []
            #         i = 0
            #         for item in hist_data:
            #             d = item.date
            #             date = datetime.strptime(item.date, '%Y%m%d %H:%M:%S')
            #             dates.append(date)
            #             values.append(item.close)
            #             counter.append(i)
            #             i += 1
            #
            #         # graph
            #
            #         penStock = pg.mkPen(color=(0, 0, 0))
            #         penProfit = pg.mkPen(color=(0, 255, 0))
            #         penLoss = pg.mkPen(color=(255, 0, 0))
            #
            #         self.graphWidget.clear()
            #         # self.graphWidget.plot( y=values, pen=penProfit)
            #         xline = [x.timestamp() for x in dates]
            #         self.graphWidget.plot(x=xline, y=values, pen=penStock, title="1 Last Hour ")
            #         self.graphWidget.setBackground('w')
            #         self.graphWidget.setTitle(values[-1], color="#d1d1e0", size="16pt")
            #         # self.graphWidget.hideAxis('bottom')

            # UI set
            self.ui.lStock.setText(stock)
            self.ui.lStock.setToolTip(description)
            self.ui.lVolume.setText(str(int(number_of_stocks)))
            self.ui.lBulckValue.setText(str(bulk_value))
            self.ui.lProfitP.setText(str(round(profit, 2)))

            # setting progressBar and percent label
            self.ui.prgProfit.setTextVisible(False)
            if profit > 0:
                self.ui.prgProfit.setMinimum(0)
                if profit >= int(settings.PROFIT):
                    self.ui.prgProfit.setMaximum(profit * 10)
                else:
                    self.ui.prgProfit.setMaximum(int(settings.PROFIT) * 10)
                self.ui.prgProfit.setValue(int(profit * 10))
                self.ui.prgProfit.setStyleSheet("QProgressBar"
                                                "{"
                                                "border: 2px solid green;"
                                                "}"
                                                "QProgressBar::chunk"
                                                "{"
                                                "background-color: green;"
                                                "}"
                                                )

                palette = self.ui.lProfitP.palette()
                palette.setColor(palette.WindowText, QtGui.QColor(51, 153, 51))
                self.ui.lProfitP.setPalette(palette)
                self.ui.lp.setPalette(palette)

            else:
                self.ui.prgProfit.setMinimum(0)
                if profit <= int(settings.LOSS):
                    self.ui.prgProfit.setMaximum(profit * -10)
                else:
                    self.ui.prgProfit.setMaximum(int(settings.LOSS) * -10)
                self.ui.prgProfit.setValue(int(profit * -10))
                self.ui.prgProfit.setStyleSheet("QProgressBar"
                                                "{"
                                                "border: 2px solid red;"
                                                "}"
                                                "QProgressBar::chunk"
                                                "{"
                                                "background-color: #F44336;"
                                                "}"
                                                )

                palette = self.ui.lProfitP.palette()
                palette.setColor(palette.WindowText, QtGui.QColor(255, 0, 0))
                self.ui.lProfitP.setPalette(palette)
                self.ui.lp.setPalette(palette)
        except Exception as e:
            if hasattr(e, 'message'):
                self.update_console("Error in updating position: " + str(e.message))
            else:
                self.update_console("Error in updating position : " + str(e))


class SettingsWindow(QDialog, Ui_setWin):

    def __init__(self):
        super().__init__()
        self.dlg = StockWindow()
        self.setupUi(self)
        # code
        self.changedSettings = False

    def setting_change(self):
        self.existingSettings.PROFIT = self.spProfit.value()
        self.existingSettings.TRAIL = self.spTrail.value()
        self.existingSettings.LOSS = self.spLoss.value()
        self.existingSettings.BULCKAMOUNT = self.spBulck.value()
        self.existingSettings.ACCOUNT = self.txtAccount.text()
        self.existingSettings.PORT = self.txtPort.text()
        self.existingSettings.INTERVALUI = self.spIntervalUi.value()
        self.existingSettings.INTERVALWORKER = self.spIntervalWorker.value()
        self.existingSettings.TECHFROMHOUR = self.tmTechFrom.time().hour()
        self.existingSettings.TECHFROMMIN = self.tmTechFrom.time().minute()
        self.existingSettings.TECHTOHOUR = self.tmTechTo.time().hour()
        self.existingSettings.TECHTOMIN = self.tmTechTo.time().minute()
        self.existingSettings.UIDEBUG = self.chbxUiDebug.isChecked()
        self.existingSettings.AUTOSTART = self.chbxAutostart.isChecked()
        self.existingSettings.USESERVER = self.chbxUseServer.isChecked()
        self.existingSettings.SERVERURL = self.txtServerUrl.text()

        self.changedSettings = True
        print("Setting was changed.")

    def showEvent(self, event):
        self.btnRemoveC.setEnabled(False)
        self.redraw_candidates_list()
        self.lstCandidates.itemClicked.connect(self.candidate_selected)
        self.lstCandidates.itemDoubleClicked.connect(self.candidate_double_clicked)

        self.spProfit.setValue(int(self.existingSettings.PROFIT))
        self.spProfit.valueChanged.connect(self.setting_change)

        self.spTrail.setValue(int(self.existingSettings.TRAIL))
        self.spTrail.valueChanged.connect(self.setting_change)

        self.spLoss.setValue(int(self.existingSettings.LOSS))
        self.spLoss.valueChanged.connect(self.setting_change)

        self.spBulck.setValue(int(self.existingSettings.BULCKAMOUNT))
        self.spBulck.valueChanged.connect(self.setting_change)

        self.txtAccount.setText(self.existingSettings.ACCOUNT)
        self.txtAccount.textChanged.connect(self.setting_change)

        self.txtPort.setText(self.existingSettings.PORT)
        self.txtPort.textChanged.connect(self.setting_change)

        self.spIntervalWorker.setValue(int(self.existingSettings.INTERVALWORKER))
        self.spIntervalWorker.valueChanged.connect(self.setting_change)

        self.spIntervalUi.setValue(int(self.existingSettings.INTERVALUI))
        self.spIntervalUi.valueChanged.connect(self.setting_change)

        self.tmTechFrom.setTime(QTime(int(self.existingSettings.TECHFROMHOUR), int(self.existingSettings.TECHFROMMIN)))
        self.tmTechFrom.timeChanged.connect(self.setting_change)

        self.tmTechTo.setTime(QTime(int(self.existingSettings.TECHTOHOUR), int(self.existingSettings.TECHTOMIN)))
        self.tmTechTo.timeChanged.connect(self.setting_change)

        self.chbxUiDebug.setChecked(self.existingSettings.UIDEBUG)
        self.chbxUiDebug.stateChanged.connect(self.setting_change)

        self.chbxAutostart.setChecked(self.existingSettings.AUTOSTART)
        self.chbxAutostart.stateChanged.connect(self.setting_change)

        self.btnRemoveC.clicked.connect(self.remove_candidate)
        self.btnAddC.clicked.connect(self.add_candidate)

        self.chbxUseServer.setChecked(self.existingSettings.USESERVER)
        self.chbxUseServer.stateChanged.connect(self.setting_change)

        self.txtServerUrl.setText(self.existingSettings.SERVERURL)
        self.txtServerUrl.textChanged.connect(self.setting_change)

        self.btnGet.clicked.connect(self.update_stocks_from_cloud)
        self.btnClear.clicked.connect(self.clear_candidates)

        self.accepted.connect(self.check_changed)

    def check_changed(self):
        if self.changedSettings:
            reply = QMessageBox.question(self, 'Settings Changed',
                                         'Accepting will cause the restart,Sure?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.No:
                self.reject()

    def redraw_candidates_list(self):
        self.lstCandidates.clear()

        for candidate in self.existingSettings.CANDIDATES:
            ticker = candidate.ticker
            reason = candidate.reason
            o = 3
            item_to_add = QListWidgetItem()
            item_to_add.setText(ticker)
            item_to_add.setToolTip(reason)
            self.lstCandidates.addItem(item_to_add)
        self.btnRemoveC.setEnabled(False)
        self.set_clear_button_state()

    def set_clear_button_state(self):
        if self.lstCandidates.count() > 0:
            self.btnClear.setEnabled(True)
        else:
            self.btnClear.setEnabled(False)

    def remove_candidate(self):
        stock_to_remove = self.lstCandidates.selectedItems()[0].text()
        for x in self.existingSettings.CANDIDATES:
            if x.ticker == stock_to_remove:
                self.existingSettings.CANDIDATES.remove(x)
                break
        self.changedSettings = True
        self.redraw_candidates_list()

    def add_candidate(self):
        self.dlg = StockWindow()
        self.dlg.client = self.ibkrClient
        self.dlg.path_to_driver = self.existingSettings.PATHTOWEBDRIVER
        if self.dlg.exec_():
            ca = SettingsCandidate()
            ca.ticker = self.dlg.txtTicker.text().upper()
            ca.reason = self.dlg.txtReason.toPlainText()
            self.existingSettings.CANDIDATES.append(ca)
            self.changedSettings = True
            self.redraw_candidates_list()
        else:
            print("Adding Canceled")

    def candidate_selected(self):
        self.btnRemoveC.setEnabled(True)

    def update_stocks_from_cloud(self):
        received_stocks = []
        try:
            x = requests.get('https://147u4tq4w4.execute-api.eu-west-3.amazonaws.com/default/ptest')
            received_stocks = json.loads(x.text)
            self.settings.CANDIDATES = received_stocks
            for s in received_stocks:
                self.lstCandidates.addItem(s['ticker'])
                i = self.lstCandidates.findItems(s['ticker'], Qt.MatchExactly)
                i[0].setToolTip(s['reason'])
            self.set_clear_button_state()
            self.setting_change()

        except:
            print('Failed to get the stocks from cloud')

    def clear_candidates(self):
        self.existingSettings.CANDIDATES = []
        self.changedSettings = True
        self.redraw_candidates_list()

    def candidate_double_clicked(self):
        stock_to_edit = self.lstCandidates.selectedItems()[0].text()
        for index, item in enumerate(self.existingSettings.CANDIDATES):
            if item.ticker == stock_to_edit:
                self.dlg = StockWindow()
                self.dlg.client = self.ibkrClient
                self.dlg.txtTicker.setText(item.ticker)
                self.dlg.txtReason.setPlainText(item.reason)
                self.dlg.path_to_driver = self.existingSettings.PATHTOWEBDRIVER
                if self.dlg.exec_():
                    ca = SettingsCandidate()
                    ca.ticker = self.dlg.txtTicker.text().upper()
                    ca.reason = self.dlg.txtReason.toPlainText()
                    self.existingSettings.CANDIDATES[index] = ca
                    self.changedSettings = True
                    self.redraw_candidates_list()
                else:
                    print("Modify Canceled")
                break


class StockWindow(QDialog, Ui_newStockDlg):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btnValidate.clicked.connect(self.validate_ticker)

    def validate_ticker(self):
        ticker = self.txtTicker.text()
        open_tip_ranks_page(ticker, self.path_to_driver)

    def addStock(self):
        ca = SettingsCandidate()
        ca.ticker = self.txtTicker
        ca.reason = self.txtReason
        self.settings.CANDIDATES.append(ca)


def main():
    app = QApplication(sys.argv)
    global settings
    settings = TraderSettings()
    global window
    window = MainWindow(settings)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
