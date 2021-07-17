import time
import threading
import datetime

from pytz import timezone



import tinvest
from tinvest import SandboxRegisterRequest, SandboxSetCurrencyBalanceRequest, SandboxSetPositionBalanceRequest


class TinkoffWorker():
    def __init__(self, settings=None):
        self.sandbox_tocken='t.NRxTfZPeWPRs-cKhC-gN44NzbWpIiKmVHvcVXCunqwuyPmRFmpGGM8IzZKu48iDqLuktAuZ9LWrjvEVF_ujIOw'
        self.real_token='t._I8-kYP_sqe8A-u357sVIkKq_06IX8-z6wCbOjvpEUvZwnxA0J-BGi3HN1bsi_r8UxowF7JX03NjgxBFHns91A'
        self.sandbox_account_id='SB3488143'
        # self.trading_session_state=None
        # self.app = IBapi()
        # self.settings = settings
        # self.app.setting = self.settings
        # self.stocks_data_from_server = []
        # self.last_worker_execution_time=None

    def run_full_cycle(self, status_callback=None, notification_callback=None):
        try:
            print("started")
            client = tinvest.SyncClient(self.real_token,use_sandbox=False)
            response = client.get_accounts()
            self.sandbox_account_id = response.payload.accounts[0].broker_account_id
            #creating sandbox account
            # body = SandboxRegisterRequest.tinkoff()
            # r=client.register_sandbox_account(body)

            #setting sandbox ballance
            # body = SandboxSetCurrencyBalanceRequest(
            #     balance=5000,
            #     currency='USD',
            # )
            # response =client.set_sandbox_currencies_balance(body, self.sandbox_account_id)
            # print(response.payload)

            #adding stocks to sandbox
            # ticker='MSFT'
            # response = client.get_market_search_by_ticker(ticker)
            # figi=response.payload.instruments[0].figi
            #
            # body = SandboxSetPositionBalanceRequest(
            #     balance=10,
            #     figi=figi,
            # )
            # client.set_sandbox_positions_balance(body, self.sandbox_account_id)

            print('All available Stocks')
            response = client.get_market_stocks()
            print(response.payload)

            #ballance
            print('Ballance')
            response = client.get_portfolio_currencies(self.sandbox_account_id)
            print(response.payload)

            #positions
            print('Portfolio')
            response = client.get_portfolio()
            for p in response.payload.positions:
                print("ticker:"+p.ticker)
                print("figi:" + p.figi)
                now = datetime.datetime.now()
                from_ = now - datetime.timedelta(days=31 * 12)
                response = client.get_operations(from_, now, p.figi, self.sandbox_account_id)
                last_operation=response.payload.operations[0]
                cur_price=p.average_position_price
                orig_price=last_operation.price
                t=3






            i=2

            # connected=self.connect_to_tws(notification_callback)
            # if connected:
            #     self.prepare_and_track( status_callback, notification_callback)
            #     self.check_if_holiday()
            #     self.process_positions_candidates( status_callback, notification_callback)
            #     return True
            # else:
            #     notification_callback.emit("Could not connect to TWS ....processing skept..")
            #     return False
        except Exception as e:
            # self.app.disconnect()
            # self.app.reset()
            # if hasattr(e, 'message'):
            #     notification_callback.emit("Error in IBKR processing : " + str(e.message))
            # else:
            #     notification_callback.emit("Error in IBKR processing : " + str(e))
            print(e)

if __name__ == '__main__':
    worker=TinkoffWorker()
    worker.run_full_cycle()