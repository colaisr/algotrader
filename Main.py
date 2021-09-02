import configparser
import json
import subprocess
import ctypes
import threading
from datetime import datetime
import setproctitle
from pytz import timezone
from AlgotraderServerConnection import report_snapshot_to_server, get_user_settings_from_server, get_command_from_server
from Logic.IBKRWorker import IBKRWorker

# The bid price refers to the highest price a buyer will pay for a security.
# The ask price refers to the lowest price a seller will accept for a security.

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

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
        print("Linux OS detected -restarting")
        import subprocess
        subprocess.call(['sh','./linux_restart_all.sh'])

    elif platform.system()=='Darwin':
        print("Mac OS detected -restarting")
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
        retrieved = get_user_settings_from_server(self.FILESERVERURL, self.FILESERVERUSER)

        self.read_config(retrieved)
        # if self.AUTORESTART:
        #     self.set_autorestart_task()
        # else:
        #     self.remove_autorestart_task()


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

    def set_autorestart_task(self):
        print("Autorestart setting applied- validating OS Setting")
        import platform
        if platform.system() == 'Windows':
            print("Windows OS detected... setting a task...")
            import os
            subprocess.call('Scripts\\win_set_autorestart.bat')
            print("Autorestart task setted")
        elif platform.system() == 'Linux':
            print("Linux is not yet implemented")
            pass
        elif platform.system() == 'Darwin':
            print("MacOS is not yet implemented")
            pass
    def remove_autorestart_task(self):
        print("Autorestart setting disabled- validating OS Setting")
        import platform
        if platform.system() == 'Windows':
            print("Windows OS detected... removing a task...")
            import os
            subprocess.call('Scripts\\win_remove_autorestart.bat')
            print("Autorestart task removed")
        elif platform.system() == 'Linux':
            print("Linux is not yet implemented")
            pass
        elif platform.system() == 'Darwin':
            print("MacOS is not yet implemented")
            pass

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
                print("Error in getting Settings: " + str(e.message))
            else:
                print("Error in getting Settings: " + str(e))
        print('Settings received.')

    def start_processing(self):
        self.process_worker()
        threading.Timer(self.settings.INTERVALSERVER, self.start_processing ).start()


    def process_worker(self):
        print("Requesting Command from server......")
        self.get_settings() #to keep them updated
        if self.settings is not None:
            server_command=get_command_from_server(self.settings)
            self.process_server_command_response(server_command)


    def process_server_command_response(self, r):
        response=json.loads(r)
        self.stocks_data_from_server=response['candidates']
        self.positions_open_on_server=response['open_positions']
        command=response['command']
        print('Received command : '+command)
        if command=='restart_worker':
            print('Restart command received- doing restart for Algotrader and TWS')
            restart_tws_and_trader()
        elif command=='close_all_positions':
            print("Closing all open positions")
            self.process_close_all_cycle()
            self.get_settings()  #to refresh a settings and cancell a BUY
        else:
            self.process_ibkr_cycle()

    def process_close_all_cycle(self):
        self.ibkrworker = IBKRWorker(self.settings)
        self.ibkrworker.close_all_positions_cycle()
        print("Worker finished reporting to the server........")

    def process_ibkr_cycle(self):
        self.ibkrworker = IBKRWorker(self.settings)
        self.ibkrworker.stocks_data_from_server = self.stocks_data_from_server
        self.ibkrworker.positions_open_on_server = self.positions_open_on_server
        successfull_cycle=self.ibkrworker.run_full_cycle()
        if not successfull_cycle:
            restart_tws_and_trader()
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
                           self.trading_session_state,
                           excess_liquidity,
                           self.started_time,
                           api_connected,
                           market_data_error,
                           tradinng_session_state]
        report_snapshot_to_server(self.settings, data_for_report)


def cmd_main():

    setproctitle.setproctitle('traderproc')

    print("Welcome to Algotrader V 6.5- client application for Algotrader platform.")
    algotrader=Algotrader()
    algotrader.get_settings()
    algotrader.start_processing()


if __name__ == '__main__':
    cmd_main()
