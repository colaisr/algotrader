import datetime

from ibapi.common import MarketDataTypeEnum
from twsapi.ibapi.contract import Contract, ContractDetails
from twsapi.ibapi.order import Order
from twsapi.ibapi.client import EClient
from twsapi.ibapi.wrapper import EWrapper


class IBapi(EWrapper, EClient):

    def __init__(self):
        EClient.__init__(self, self)
        self.openPositions={}
        self.positionDetails = {}
        self.openOrders={}
        self.candidates={}
        self.excessLiquidity=""


    # def error(self, reqId: int, errorCode: int, errorString: str):
    #     if reqId > -1:
    #         print("Error. Id: ", reqId, " Code: ", errorCode, " Msg: ", errorString)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)


    def pnl(self, reqId: int, dailyPnL: float,unrealizedPnL: float, realizedPnL: float):
        super().pnl(reqId, dailyPnL, unrealizedPnL, realizedPnL)
        self.generalStatus="DailyPnL:"+str(dailyPnL)+"UnrealizedPnL:"+ str(unrealizedPnL)+ "RealizedPnL:"+ str(realizedPnL)
        # print("PnL today status: ")
        # print(self.generalStatus)

    def pnlSingle(self, reqId: int, pos: int, dailyPnL: float,unrealizedPnL: float, realizedPnL: float, value: float):
        super().pnlSingle(reqId, pos, dailyPnL, unrealizedPnL, realizedPnL, value)

        self.positionDetails[reqId]= { "Stock":self.positionDetails[reqId]["Stock"],
              "Position":pos,
              "DailyPnL": dailyPnL,
              "UnrealizedPnL": unrealizedPnL,
              "RealizedPnL": realizedPnL,
              "Value": value}
        # print("Daily PnL Single. ReqId:", reqId,
        #       "Stock:",self.positionDetails[reqId]["Stock"],
        #       "Position:", pos,
        #       "DailyPnL:", dailyPnL,
        #       "UnrealizedPnL:", unrealizedPnL,
        #       "RealizedPnL:", realizedPnL,
        #       "Value:", value)


    def position(self, account: str, contract: Contract, position: float,avgCost: float):
        super().position(account, contract, position, avgCost)
        self.openPositions[contract.symbol]={"stocks":position,"cost":avgCost,"conId":contract.conId}
        # print("Symbol:", contract.symbol,"Stocks:", position, "Avg cost:", avgCost,"Added to the list")


    def positionEnd(self):
        super().positionEnd()
        print(len(self.openPositions),"Open Positions found")

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice):
        super().orderStatus(orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice)
        # print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining,
        #       'lastFillPrice', lastFillPrice)

    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        self.openOrders[contract.symbol] = {"Action": order.action, "Type": order.orderType}
        # print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action,
        #       order.orderType, order.totalQuantity, orderState.status)

    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)
        # print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId,
        #       execution.orderId, execution.shares, execution.lastLiquidity)

    def tickPrice(self, reqId, tickType, price, attrib):
        super().tickPrice(reqId, tickType, price, attrib)
        if tickType==1:
            self.candidates[reqId]["Bid"] =price
            # self.candidates[reqId] = {"Stock": self.candidates[reqId]["Stock"],
            #                           "Close": self.candidates[reqId]["Close"],
            #                           "Bid": price,
            #                           "Ask": self.candidates[reqId]["Ask"],
            #                           "LastPrice": self.candidates[reqId]["LastPrice"],
            #                           }
        elif tickType==2:
            self.candidates[reqId]["Ask"] = price
            # self.candidates[reqId] = {"Stock": self.candidates[reqId]["Stock"],
            #                           "Close": self.candidates[reqId]["Close"],
            #                           "Bid": self.candidates[reqId]["Bid"],
            #                           "Ask": price,
            #                           "LastPrice": self.candidates[reqId]["LastPrice"],
            #                           }
        elif tickType==4:
            self.candidates[reqId]["LastPrice"] = price
            # self.candidates[reqId] = {"Stock": self.candidates[reqId]["Stock"],
            #                           "Close": self.candidates[reqId]["Close"],
            #                           "Bid": self.candidates[reqId]["Bid"],
            #                           "Ask": self.candidates[reqId]["Ask"],
            #                           "LastPrice": price,
            #                           }
        elif tickType==9:
            self.candidates[reqId]["Close"] = price
            # self.candidates[reqId] = {"Stock": self.candidates[reqId]["Stock"],
            #                           "Close": price,
            #                           "Bid": self.candidates[reqId]["Bid"],
            #                           "Ask": self.candidates[reqId]["Ask"],
            #                           "LastPrice": self.candidates[reqId]["LastPrice"],
            #                           }
        else:
            print("unrecognized tick")

        self.candidates[reqId]["LastUpdate"] = datetime.datetime.now()
        # self.candidates[reqId]= { "Stock":self.positionDetails[reqId]["Stock"],
        #       "Close":self.candidates[reqId]["Close"],
        #       "Bid": self.candidates[reqId]["Bid"],
        #       "Ask": self.candidates[reqId]["Ask"],
        #       "LastPrice": self.candidates[reqId]["LastPrice"],
        #       "LastUpdate": datetime.now()
        #       }


    def accountSummary(self, reqId: int, account: str, tag: str, value: str,
                        currency: str):
         super().accountSummary(reqId, account, tag, value, currency)
         self.excessLiquidity=value




def createContract(symbol:str):
    # Create contract object
    newContract = Contract()
    newContract.symbol = symbol
    newContract.secType = 'STK'
    newContract.exchange = 'SMART'
    newContract.primaryExchange = 'ISLAND'
    newContract.currency = 'USD'
    return newContract

def createTrailingStopOrder(quantity,trailPercent):

    # Create order object
    order = Order()
    order.action = 'SELL'
    order.orderType = 'TRAIL'
    order.totalQuantity = quantity
    order.trailingPercent = float(trailPercent);
    order.tif='GTC'

def createLMTbuyorder(quantity, lmtPrice):
    # Create order object
    order = Order()
    order.action = 'BUY'
    order.orderType = 'LMT'
    order.totalQuantity = quantity
    order.lmtPrice = float(lmtPrice);
    order.tif = 'GTC'


    return order
