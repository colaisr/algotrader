import datetime
from AlgotraderServerConnection import report_market_action
from ibapi.common import MarketDataTypeEnum, HistogramDataList, BarData
from twsapi.ibapi.contract import Contract, ContractDetails
from twsapi.ibapi.order import Order
from twsapi.ibapi.client import EClient
from twsapi.ibapi.wrapper import EWrapper


class IBapi(EWrapper, EClient):

    def __init__(self):
        EClient.__init__(self, self)
        self.openPositions = {}
        self.openPositionsLiveDataRequests = {}
        self.temp_positions={}
        self.openOrders = {}
        self.candidatesLive = {}
        self.openPositionsHistolicalData={}
        self.generalStatus = "PnL not yet received"
        self.dailyPnl =0
        self.finishedPostitionsGeneral=False
        self.finishedReceivingOrders=False
        self.openPositionsLiveHistoryRequests={}
        self.excessLiquidity = 0
        self.sMa=0
        self.tradesRemaining=0
        self.netLiquidation=0
        self.contract_processing=False
        self.setting=None
        self.trading_session=''
        self.trading_hours_received=False


    # def error(self, reqId: int, errorCode: int, errorString: str):
    #     if reqId > -1:
    #         print("Error. Id: ", reqId, " Code: ", errorCode, " Msg: ", errorString)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId

    def pnl(self, reqId: int, dailyPnL: float, unrealizedPnL: float, realizedPnL: float):
        super().pnl(reqId, dailyPnL, unrealizedPnL, realizedPnL)

        self.generalStatus = "DailyPnL: " + str(dailyPnL) + " UnrealizedPnL: " + str(
            unrealizedPnL) + " RealizedPnL: " + str(realizedPnL)
        self.dailyPnl=dailyPnL
        print("PNL status updated:"+self.generalStatus)

    def pnlSingle(self, reqId: int, pos: int, dailyPnL: float, unrealizedPnL: float, realizedPnL: float, value: float):
        super().pnlSingle(reqId, pos, dailyPnL, unrealizedPnL, realizedPnL, value)


        if reqId in self.openPositionsLiveDataRequests.keys():
            print("position key is in requests- updating")
            s = self.openPositionsLiveDataRequests[reqId]
            t=self.temp_positions[s]
            self.openPositions[s]={}
            self.openPositions[s]["stocks"] = pos
            self.openPositions[s]["cost"] = t['cost']
            self.openPositions[s]["conId"] = t['conId']
            self.openPositions[s]["HistoricalData"] = []
            self.openPositions[s]["DailyPnL"] = dailyPnL
            self.openPositions[s]["UnrealizedPnL"] = unrealizedPnL
            self.openPositions[s]["RealizedPnL"] = realizedPnL
            self.openPositions[s]["Value"] = value
            self.openPositions[s]["LastUpdate"] = datetime.datetime.now()
            print("detailed position updated for request",str(reqId))
        else:
            print(str(reqId)+" detailed position not found cancelling the requests")
            self.cancelPnLSingle(reqId);  # cancel subscription after getting
        self.have_empty_values_in_positions = False
        for c, v in self.openPositions.items():
            if 'Value' not in v.keys():
                self.have_empty_values_in_positions = True

    def position(self, account: str, contract: Contract, position: float, avgCost: float):
        super().position(account, contract, position, avgCost)
        self.temp_positions[contract.symbol] = {"stocks": position, "cost": avgCost, "conId": contract.conId,"HistoricalData":[]}
        # self.openPositions[contract.symbol] = {"stocks": position, "cost": avgCost, "conId": contract.conId,"HistoricalData":[]}
        print("Position general data received.", "Account:", account, "Symbol:", contract.symbol, "SecType:",contract.secType, "Currency:", contract.currency,contract.secType, "Currency:", contract.currency,"Position:", position, "Avg cost:", avgCost)

    def positionEnd(self):
        super().positionEnd()
        self.finishedPostitionsGeneral=True
        print("Finished getting ", len(self.openPositions), " open Positions General info - requesting data per each position")

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice):
        super().orderStatus(orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId,
                            whyHeld, mktCapPrice)
        # sentence='!!!orderStatus - orderid:'+str(orderId)+'status:'+ status+ 'filled'+ str(filled) +'remaining'+ str(remaining)+'lastFillPrice'+ str(lastFillPrice)
        # self.log_decision("testingOrderStatus", sentence)
        # self.log_decision("testingMix", sentence)
        # print('!!!orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining,
        #       'lastFillPrice', lastFillPrice)

    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        self.openOrders[contract.symbol] = {"Action": order.action, "Type": order.orderType,"OrderId":orderId}
        print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action,
              order.orderType, order.totalQuantity, orderState.status)

    def openOrderEnd(self):
        super().openOrderEnd()
        self.finishedReceivingOrders=True
        print("Finished getting ", len(self.openOrders), " open Orders")

    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)
        #important
        symbol=contract.symbol
        shares=execution.shares
        price=execution.price
        time=execution.time
        side=execution.side       #sell SLD   buy BOT
        self.report_execution_to_Server(symbol,shares,price,side,time)
        # sentence='???execDetails Order Executed: '+ " request id: "+str(reqId)+" contract.symbol:"+contract.symbol+ " contract.sectype:"+contract.secType+" contract currency:"+contract.currency+" execution.execId:"+str(execution.execId)+"execution.orderId:"+str(execution.orderId)+"execution shares:"+str(execution.shares)+ "execution.lastliquidity:"+str(execution.lastLiquidity)
        # self.log_decision("testingExecDetails",sentence)
        # self.log_decision("testingMix", sentence)
        # print('???execDetails Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency,
        #       execution.execId,
        #       execution.orderId, execution.shares, execution.lastLiquidity)

    def tickPrice(self, reqId, tickType, price, attrib):
        super().tickPrice(reqId, tickType, price, attrib)
        # print("Tick received")
        if tickType == 1:
            self.candidatesLive[reqId]["Bid"] = price
        elif tickType == 2:
            self.candidatesLive[reqId]["Ask"] = price
        elif tickType == 4:
            #last price ignored - have no value
            return
        elif tickType == 9:
            self.candidatesLive[reqId]["Close"] = price
        elif tickType == 6:
            return
            # self.candidatesLive[reqId]["High"] = price
        elif tickType == 7:
            # self.candidatesLive[reqId]["Low"] = price
            return
        elif tickType == 14:
            self.candidatesLive[reqId]["Open"] = price
        else:
            print("unrecognized tick:", tickType)

        self.candidatesLive[reqId]["LastUpdate"] = datetime.datetime.now()

    def accountSummary(self, reqId: int, account: str, tag: str, value: str,
                       currency: str):
        super().accountSummary(reqId, account, tag, value, currency)
        print("Account summary received")
        if tag=='DayTradesRemaining':
            self.tradesRemaining=int(value)
        elif tag=='ExcessLiquidity':
            self.excessLiquidity=float(value)
        elif tag=='SMA':
            self.sMa=float(value)
        elif tag=="NetLiquidation":
            self.netLiquidation=float(value)

        print("AccountSummary. ReqId:", reqId, "Account:", account,"Tag: ", tag, "Value:", value, "Currency:", currency)

    def historicalData(self, reqId: int, bar: BarData):
        if reqId in self.openPositionsLiveHistoryRequests.keys():
            s = self.openPositionsLiveHistoryRequests[reqId]
            self.openPositions[s]["HistoricalData"].append(bar)

            print("HistoricalData. ", reqId, " Date:", bar.date, "Open:", bar.open,
                  "High:", bar.high, "Low:", bar.low, "Close:", bar.close, "Volume:", bar.volume,
                  "Count:", bar.barCount, "WAP:", bar.average)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)
        del self.openPositionsLiveHistoryRequests[reqId]
        print("HistoricalDataEnd ", reqId, "from", start, "to", end)

    def historicalDataUpdate(self, reqId: int, bar: BarData):
        s = self.openPositionsLiveHistoryRequests[reqId]
        self.openPositions[s]["HistoricalData"][-1]=bar
        print("HistoricalDataUpdate. ", reqId, " Date:", bar.date, "Open:", bar.open,
              "High:", bar.high, "Low:", bar.low, "Close:", bar.close, "Volume:", bar.volume,
              "Count:", bar.barCount, "WAP:", bar.average)

    def contractDetails(self, reqId: int, contractDetails: ContractDetails):
        super().contractDetails(reqId, contractDetails)
        # self.contractDetailsList[reqId]= contractDetails
        # self.contract_processing = False
        self.trading_session=contractDetails.tradingHours
        self.trading_hours_received=True

    def contractDetailsEnd(self, reqId: int):
        super().contractDetailsEnd(reqId)

    def log_decision(self, logFile, order):
        with open(logFile, "a") as f:
            currentDt = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            order = currentDt + '---' + order+"\n"
            f.write(order)

    def report_execution_to_Server(self, symbol, shares, price, side, time):
        report_market_action(self.setting,symbol, shares, price, side, time)


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
