import datetime
import time

from AlgotraderServerConnection import report_market_action
from ibapi.common import MarketDataTypeEnum, HistogramDataList, BarData, TickerId
from twsapi.ibapi.contract import Contract, ContractDetails
from twsapi.ibapi.order import Order
from twsapi.ibapi.client import EClient
from twsapi.ibapi.wrapper import EWrapper


class IBapi(EWrapper, EClient):

    def __init__(self):
        EClient.__init__(self, self)
        self.openPositions = {}
        self.openPositionsLiveDataRequests = {}
        self.temp_positions = {}
        self.openOrders = {}
        self.candidatesLive = {}
        self.openPositionsHistolicalData = {}
        self.generalStatus = "PnL not yet received"
        self.dailyPnl = 0
        self.finishedPostitionsGeneral = False
        self.finishedReceivingOrders = False
        self.openPositionsLiveHistoryRequests = {}
        self.excessLiquidity = 0
        self.sMa = 0
        self.tradesRemaining = 0
        self.netLiquidation = 0
        self.contract_processing = False
        self.setting = None
        self.trading_session = ''
        self.trading_hours_received = False
        self.executions_received = False
        self.market_data_error = False
        self.reports_lst = {}

    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        # super().error(reqId, errorCode, errorString)
        if errorCode == 2104 or errorCode == 2106 or errorCode == 2158 or errorCode == 2108 or errorCode == 2119 or errorCode == 2157:
            # ok messages
            pass
        elif errorCode == 502:
            pass
        elif errorCode == 202:
            print("All active orders cancelled")
        elif errorCode == 0:  # approaching 50 messages code - wait 1 sec to clean
            time.sleep(90)
        elif errorCode == 2101 or errorCode == 2110 or errorCode == 1100:  # another connection created restartto work on disconnect
            print("connection with a station was lost- restarting after 90 seconds")
            time.sleep(90)
            cmd = 'reboot &'
            import os
            os.system(cmd)
        else:  # requested market data is not subscribed or other problem
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!need to be handled- error code :" + str(
                errorCode) + "   " + errorString)
            try:
                if self.CandidatesLiveDataRequests is not None:
                    if reqId in self.CandidatesLiveDataRequests.keys():
                        self.cancelMktData(reqId)
                        del self.CandidatesLiveDataRequests[reqId]
                    if reqId in self.candidatesLive.keys():
                        del self.candidatesLive[reqId]
                    print("ERROR in DATA: " + str(errorCode))
                else:
                    print("connection with a station was lost- restarting")
                    import subprocess
                    subprocess.call(['sh', './linux_restart_all.sh'])
            except AttributeError:
                pass
                self.market_data_error = True

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId

    def pnl(self, reqId: int, dailyPnL: float, unrealizedPnL: float, realizedPnL: float):
        super().pnl(reqId, dailyPnL, unrealizedPnL, realizedPnL)

        self.generalStatus = "DailyPnL: " + str(dailyPnL) + " UnrealizedPnL: " + str(
            unrealizedPnL) + " RealizedPnL: " + str(realizedPnL)
        self.dailyPnl = dailyPnL

    def pnlSingle(self, reqId: int, pos: int, dailyPnL: float, unrealizedPnL: float, realizedPnL: float, value: float):
        super().pnlSingle(reqId, pos, dailyPnL, unrealizedPnL, realizedPnL, value)
        if reqId in self.openPositionsLiveDataRequests.keys():
            s = self.openPositionsLiveDataRequests[reqId]
            t = self.temp_positions[s]
            self.openPositions[s] = {}
            self.openPositions[s]["stocks"] = pos
            self.openPositions[s]["cost"] = t['cost']
            self.openPositions[s]["conId"] = t['conId']
            self.openPositions[s]["HistoricalData"] = []
            self.openPositions[s]["DailyPnL"] = dailyPnL
            self.openPositions[s]["UnrealizedPnL"] = unrealizedPnL
            self.openPositions[s]["RealizedPnL"] = realizedPnL
            self.openPositions[s]["Value"] = value
            self.openPositions[s]["LastUpdate"] = datetime.datetime.now()
            print('pnl details received for request:' + str(reqId))  # debug only
            self.cancelPnLSingle(reqId)
            self.openPositionsLiveDataRequests.pop(reqId, None)

    def position(self, account: str, contract: Contract, position: float, avgCost: float):
        super().position(account, contract, position, avgCost)
        self.temp_positions[contract.symbol] = {"stocks": position, "cost": avgCost, "conId": contract.conId,
                                                "HistoricalData": []}

    def positionEnd(self):
        super().positionEnd()
        self.finishedPostitionsGeneral = True

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice):
        super().orderStatus(orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId,
                            whyHeld, mktCapPrice)

    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        self.openOrders[contract.symbol] = {"Action": order.action,
                                            "Type": order.orderType,
                                            "adjustedStopPrice": order.trailStopPrice,
                                            "OrderId": orderId}

    def openOrderEnd(self):
        super().openOrderEnd()
        self.finishedReceivingOrders = True

    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)
        # important
        symbol = contract.symbol
        shares = execution.shares
        price = execution.price
        time = execution.time
        side = execution.side  # sell SLD   buy BOT
        order_id = execution.orderId
        execution_id = execution.execId
        print("Execution reported for " + symbol + " Stocks:" + str(shares) + " at " + str(
            time) + " side " + side + " order: " + str(order_id) + "exec_id: " + str(execution_id))

        if symbol in self.reports_lst:
            self.reports_lst[symbol]['shares'] += shares
        else:
            self.reports_lst[symbol] = {'shares': shares, 'price': price, 'side': side, 'time': time, 'id': execution_id}
        # self.report_execution_to_Server(symbol, shares, price, side, time, execution_id)

    def execDetailsEnd(self, reqId: int):
        for key, value in self.reports_lst.items():
            self.report_execution_to_Server(key, value['shares'], value['price'], value['side'], value['time'], value['id'])
        super().execDetailsEnd(reqId)
        self.executions_received = True

    def tickPrice(self, reqId, tickType, price, attrib):
        super().tickPrice(reqId, tickType, price, attrib)
        if tickType == 1:
            self.candidatesLive[reqId]["Bid"] = price
            if (self.candidatesLive[reqId]["Ask"] != 0 and self.candidatesLive[reqId]["Close"] != 0):
                if self.trading_session_state == 'Open':
                    if self.candidatesLive[reqId]["Open"] != 0:
                        if reqId in self.CandidatesLiveDataRequests.keys():
                            self.cancelMktData(reqId)
                            del self.CandidatesLiveDataRequests[reqId]

                            print("Got data, stopped tracking request " + str(reqId))
                else:
                    if reqId in self.CandidatesLiveDataRequests.keys():
                        self.cancelMktData(reqId)
                        del self.CandidatesLiveDataRequests[reqId]
                        print("Got data, stopped tracking request " + str(reqId))
        elif tickType == 2:
            self.candidatesLive[reqId]["Ask"] = price
            if (self.candidatesLive[reqId]["Bid"] != 0 and self.candidatesLive[reqId]["Close"] != 0):
                if self.trading_session_state == 'Open':
                    if self.candidatesLive[reqId]["Open"] != 0:
                        if reqId in self.CandidatesLiveDataRequests.keys():
                            self.cancelMktData(reqId)
                            del self.CandidatesLiveDataRequests[reqId]
                            print("Got data, stopped tracking request " + str(reqId))
                else:
                    if reqId in self.CandidatesLiveDataRequests.keys():
                        self.cancelMktData(reqId)
                        del self.CandidatesLiveDataRequests[reqId]
                        print("Got data, stopped tracking request " + str(reqId))
        elif tickType == 4:
            # last price ignored - have no value
            return
        elif tickType == 9:
            self.candidatesLive[reqId]["Close"] = price
            if (self.candidatesLive[reqId]["Bid"] != 0 and self.candidatesLive[reqId]["Ask"] != 0):
                if self.trading_session_state == 'Open':
                    if self.candidatesLive[reqId]["Open"] != 0:
                        if reqId in self.CandidatesLiveDataRequests.keys():
                            self.cancelMktData(reqId)
                            del self.CandidatesLiveDataRequests[reqId]
                            print("Got data, stopped tracking request " + str(reqId))
                else:
                    if reqId in self.CandidatesLiveDataRequests.keys():
                        self.cancelMktData(reqId)
                        del self.CandidatesLiveDataRequests[reqId]
                    print("Got data, stopped tracking request " + str(reqId))
        elif tickType == 6:
            return
            # self.candidatesLive[reqId]["High"] = price
        elif tickType == 7:
            # self.candidatesLive[reqId]["Low"] = price
            return
        elif tickType == 14:
            self.candidatesLive[reqId]["Open"] = price
            if (self.candidatesLive[reqId]["Bid"] != 0 and self.candidatesLive[reqId]["Ask"] != 0 and
                    self.candidatesLive[reqId]["Close"] != 0):
                if reqId in self.CandidatesLiveDataRequests.keys():
                    self.cancelMktData(reqId)
                    del self.CandidatesLiveDataRequests[reqId]
                print("Got data, stopped tracking request " + str(reqId))
        else:
            print("unrecognized tick:", tickType)

        self.candidatesLive[reqId]["LastUpdate"] = datetime.datetime.now()

    def accountSummary(self, reqId: int, account: str, tag: str, value: str,
                       currency: str):
        super().accountSummary(reqId, account, tag, value, currency)
        if tag == 'DayTradesRemaining':
            self.tradesRemaining = int(value)
        elif tag == 'ExcessLiquidity':
            self.excessLiquidity = float(value)
        elif tag == 'SMA':
            self.sMa = float(value)
        elif tag == "NetLiquidation":
            self.netLiquidation = float(value)

    def historicalData(self, reqId: int, bar: BarData):
        if reqId in self.openPositionsLiveHistoryRequests.keys():
            s = self.openPositionsLiveHistoryRequests[reqId]
            self.openPositions[s]["HistoricalData"].append(bar)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        del self.openPositionsLiveHistoryRequests[reqId]

    def historicalDataUpdate(self, reqId: int, bar: BarData):
        s = self.openPositionsLiveHistoryRequests[reqId]
        self.openPositions[s]["HistoricalData"][-1] = bar

    def contractDetails(self, reqId: int, contractDetails: ContractDetails):
        super().contractDetails(reqId, contractDetails)
        self.trading_session = contractDetails.tradingHours
        self.trading_hours_received = True

    def contractDetailsEnd(self, reqId: int):
        super().contractDetailsEnd(reqId)

    def report_execution_to_Server(self, symbol, shares, price, side, time, exec_id):
        report_market_action(self.setting, symbol, shares, price, side, time, exec_id)


def createContract(symbol: str):
    # Create contract object
    newContract = Contract()
    newContract.symbol = symbol
    newContract.secType = 'STK'
    newContract.exchange = 'SMART'
    newContract.primaryExchange = 'ISLAND'
    newContract.currency = 'USD'
    return newContract


def createTrailingStopOrder(quantity, trailPercent):
    # Create order object
    order = Order()
    order.action = 'SELL'
    order.orderType = 'TRAIL'
    order.totalQuantity = quantity
    order.trailingPercent = float(trailPercent);
    order.tif = 'GTC'

    return order


def createMktSellOrder(quantity):
    # Create order object
    order = Order()
    order.action = 'SELL'
    order.orderType = 'MKT'
    order.totalQuantity = quantity
    order.tif = 'GTC'

    return order


def create_limit_buy_order(quantity, lmtPrice):
    # Create order object
    order = Order()
    order.action = 'BUY'
    order.orderType = 'LMT'
    order.totalQuantity = quantity
    order.lmtPrice = float(lmtPrice);
    order.tif = 'GTC'

    return order
