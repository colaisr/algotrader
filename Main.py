import os
import sys
import time

import logging
import logging.config

from Scripts.tws_cred_login import login_tws_user

client_version=7.5
import configparser
import json
import threading
from datetime import datetime
import setproctitle
from pytz import timezone
from AlgotraderServerConnection import report_snapshot_to_server, get_user_settings_from_server, get_command_from_server
from Logic.IBKRWorker import IBKRWorker
import psutil

class LoggerWriter:
    def __init__(self,settings):
        LOGGING = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'logzioFormat': {
                    'format': '{"additional_field": "value"}',
                    'validate': False
                }
            },
            'handlers': {
                'logzio': {
                    'class': 'logzio.handler.LogzioHandler',
                    'level': 'INFO',
                    'formatter': 'logzioFormat',
                    'token': 'LqXYrBEPOxfEBTGumvPhxXljqvNDadbf',
                    'logzio_type': '<<LOG-TYPE>>',
                    'logs_drain_timeout': 5,
                    'url': 'https://listener-eu.logz.io:8071'
                }
            },
            'loggers': {
                '': {
                    'level': 'DEBUG',
                    'handlers': ['logzio'],
                    'propagate': True
                }
            }
        }
        logging.config.dictConfig(LOGGING)
        self.logger = logging.getLogger(__name__)
        self.user=settings.FILESERVERUSER


    def write(self, message):
        if message != '\n':
            print(message)
            self.logger.info(message, extra={'user':self.user})
    def flush(self):
        pass


class Algotrader_logger:
    def __init__(self,settings):
        self.user=settings.SERVERUSER
        self.logger=''
        self.set_remote_logger()

    def set_remote_logger(self):

        LOGGING = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'logzioFormat': {
                    'format': '{"additional_field": "value"}',
                    'validate': False
                }
            },
            'handlers': {
                'logzio': {
                    'class': 'logzio.handler.LogzioHandler',
                    'level': 'INFO',
                    'formatter': 'logzioFormat',
                    'token': 'LqXYrBEPOxfEBTGumvPhxXljqvNDadbf',
                    'logzio_type': '<<LOG-TYPE>>',
                    'logs_drain_timeout': 5,
                    'url': 'https://listener-eu.logz.io:8071'
                }
            },
            'loggers': {
                '': {
                    'level': 'INFO',
                    'handlers': ['logzio'],
                    'propagate': True
                }
            }
        }
        logging.config.dictConfig(LOGGING)
        self.logger = logging.getLogger(__name__)

    def log(self,message):
        print(message)
        self.logger.info(message, extra={'user':self.user})

# The bid price refers to the highest price a buyer will pay for a security.
# The ask price refers to the lowest price a seller will accept for a security.

def checkIfProcessRunning(processName):
    '''
    Check if there is any running process that contains the given name processName.
    '''
    #Iterate over the all the running process
    for proc in psutil.process_iter(['pid', 'name','username']):
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            print('exception in checking for process exist to start TWS')
    return False;


def restart_tws_and_trader():
    import platform
    if platform.system()=='Windows':
        import sys
        print("Windows OS detected -restarting")
        print("argv was", sys.argv)
        print("sys.executable was", sys.executable)
        print("restart now")
        import subprocess
        import os
        subprocess.call('Scripts\\win_restartTws.bat')
        os.execv(sys.executable, ['python'] + sys.argv)
    elif platform.system()=='Linux':
        al.log("Linux OS detected -restarting")

        cmd = 'reboot &'
        import os
        os.system(cmd)

    elif platform.system()=='Darwin':
        al.log("Mac OS detected -restarting")

        import sys
        import os
        os.execl(sys.executable, sys.executable, *sys.argv)


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
        self.TWSSTARTCOMMAND = self.config['Server']['tws_installation_pathl']


        retrieved = get_user_settings_from_server(self.FILESERVERURL, self.FILESERVERUSER)
        self.read_config(retrieved)
        global al
        al = Algotrader_logger(self)


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
        self.ALLOWSELL = retrieved['algo_allow_sell']
        self.AUTORESTART = retrieved['station_autorestart']
        self.APPLYMAXHOLD=retrieved['algo_apply_max_hold']
        self.MAXHOLDDAYS=retrieved['algo_max_hold_days']
        self.TWSUSER = retrieved['connection_tws_user']
        self.TWSPASS = retrieved['connection_tws_pass']


class Algotrader:
    def __init__(self):
        self.trading_session_state = "TBD"
        self.trading_time_zone = timezone('US/Eastern')

        self.settings = None
        self.stocks_data_from_server =None
        self.positions_open_on_server = None
        self.started_time=datetime.now()

    def get_settings(self):
        print('Connecting to server - to get settings.')
        self.settings=None
        try:
            self.settings=TraderSettings()
        except Exception as e:
            if hasattr(e, 'message'):
                al.log("Error in getting Settings: " + str(e.message))

            else:
                al.log("Error in getting Settings: " + str(e))
        al.log('Settings received.')

    def start_processing(self):
        self.process_worker()
        threading.Timer(self.settings.INTERVALSERVER, self.start_processing ).start()

    def process_worker(self):
        al.log("Requesting Command from server......")

        self.get_settings() #to keep them updated
        if self.settings is not None:
            server_command=get_command_from_server(self.settings)
            self.process_server_command_response(server_command)

    def process_server_command_response(self, r):
        response=json.loads(r)
        self.stocks_data_from_server=response['candidates']
        self.positions_open_on_server=response['open_positions']
        command=response['command']
        al.log('Received command : '+command)

        if command=='restart_worker':
            al.log('Restart command received- doing restart for Algotrader and TWS')

            restart_tws_and_trader()
        elif command=='close_all_positions':
            al.log("Closing all open positions")

            self.process_close_all_cycle()
            self.get_settings()  #to refresh a settings and cancell a BUY
        else:
            self.process_ibkr_cycle()

    def process_close_all_cycle(self):
        self.ibkrworker = IBKRWorker(self.settings,logger=al)
        self.ibkrworker.close_all_positions_cycle()
        al.log("Worker finished reporting to the server........")


    def process_ibkr_cycle(self):
        self.ibkrworker = IBKRWorker(self.settings,logger=al)
        self.ibkrworker.stocks_data_from_server = self.stocks_data_from_server
        self.ibkrworker.positions_open_on_server = self.positions_open_on_server
        successfull_cycle=self.ibkrworker.run_full_cycle()
        if not successfull_cycle:
            restart_tws_and_trader()
        al.log("Worker finished reporting to the server........")

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
        tradinng_session_state = self.ibkrworker.trading_session_state
        worker_last_execution = self.ibkrworker.last_worker_execution_time
        api_connected=self.ibkrworker.api_connected
        market_data_error = self.ibkrworker.app.market_data_error
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
                           tradinng_session_state,
                           excess_liquidity,
                           self.started_time,
                           api_connected,
                           market_data_error,
                           client_version]
        report_snapshot_to_server(self.settings, data_for_report)
        self.ibkrworker.app.disconnect()

    def start_tws(self,settings):
        tws_running=checkIfProcessRunning('JavaApplicationStub')
        user=str(os.environ._data)
        if 'colakamornik' not in user:
            al.log('Starting TWS configured in INI file')

            cmd=settings.TWSSTARTCOMMAND
            os.system(cmd)
            while not checkIfProcessRunning('pxgsettings'):
                al.log('Waiting for login Screen')
                time.sleep(1)
            al.log("TWS process found starting login")
            login_tws_user(settings)


def cmd_main():


    setproctitle.setproctitle('traderproc')
    algotrader=Algotrader()
    algotrader.get_settings()
    # sys.stderr = LoggerWriter(algotrader.settings)  # this is redirecting output to remote directly
    al.log('Client started V:'+str(client_version))
    algotrader.start_tws(algotrader.settings)
    algotrader.start_processing()


if __name__ == '__main__':
    cmd_main()
