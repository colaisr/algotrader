

import configparser
import json
import subprocess
import sys
import threading
import traceback
from datetime import datetime
from sys import platform


import os

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


class Algotrader:
    def __init__(self):
        self.trading_session_state = "TBD"
        self.trading_time_zone = timezone('US/Eastern')

        self.settings = None
        self.stocks_data_from_server =None
        self.started_time=datetime.now()

    def get_settings(self):
        print('Connecting to server - to get settings.')
        self.settings=TraderSettings()
        print('Settings received.')

    def start_processing(self):
        self.process_worker()
        threading.Timer(self.settings.INTERVALSERVER, self.start_processing ).start()


    def process_worker(self):
        print("Requesting Command from server......")
        server_command=get_command_from_server(self.settings)
        self.process_server_command_response(server_command)


    def process_server_command_response(self, r):
        response=json.loads(r)
        self.stocks_data_from_server=response['candidates']
        command=response['command']
        print('Received command : '+command)
        if command=='restart_worker':
            print('Restart command received- doing restart for Algotrader and TWS')
            restart_tws_and_trader()
        else:
            self.process_ibkr_cycle()


    def process_ibkr_cycle(self):
        self.ibkrworker = IBKRWorker(self.settings)
        self.ibkrworker.stocks_data_from_server = self.stocks_data_from_server
        self.ibkrworker.run_full_cycle()
        print("Worker finished reporting to the server........")
        self.report_to_server()


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
                           excess_liquidity,
                           self.started_time]
        report_snapshot_to_server(self.settings, data_for_report)


def cmd_main():
    print("Welcome to Algotrader V 5.0- client application for Algotrader platform.")
    algotrader=Algotrader()
    algotrader.get_settings()
    algotrader.start_processing()


if __name__ == '__main__':
    cmd_main()
