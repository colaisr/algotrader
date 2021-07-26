import time
import threading
import datetime

from pytz import timezone

import tinvest



class TinkoffWorker():
    def __init__(self, settings=None):
        self.sandbox_token_='t.AtZrypPg5QvIS3HkVpHaDjcD4lDcy_PWlD6rr4ir3htS0qjBIHMQzj8DaTzDIm2-6BZCsaszFqfjaX6iXsSkOg'
        self.real_token='t.gCaA5F8YcGPFm91pMCRPXuKMgH2nxlqbb-L4hMx1kE-ezBOF_jYu0PMrN2nyY-Z6uob148nPU_fOm4KFm75bJQ'
        self.client = tinvest.SyncClient(self.real_token)
        self.sandbox_client=tinvest.SyncClient(self.sandbox_token_,use_sandbox=True)

        self.sandbox_account_id='SB3488143'

    def get_real_portfolio(self):
        try:
            response = self.client.get_portfolio()
            print(response.payload)
        except tinvest.BadRequestError as e:
            print(e.response)  # tinvest.Error

    def get_sandbox_portfolio(self):
        try:
            response = self.sandbox_client.get_portfolio()
            print(response.payload)
        except tinvest.BadRequestError as e:
            print(e.response)

    def get_sandbox_accounts(self):
        try:
            response = self.sandbox_client.get_accounts()
            print(response.payload)
        except tinvest.BadRequestError as e:
            print(e.response)

    def get_real_accounts(self):
        try:
            response = self.client.get_accounts()
            print(response.payload)
        except tinvest.BadRequestError as e:
            print(e.response)

if __name__ == '__main__':
    worker=TinkoffWorker()
    worker.get_sandbox_portfolio()