from ibapi.common import MarketDataTypeEnum
from twsapi.ibapi.contract import Contract, ContractDetails
from twsapi.ibapi.order import Order
from twsapi.ibapi.client import EClient
from twsapi.ibapi.wrapper import EWrapper


class IBapi(EWrapper, EClient):

    def __init__(self):
        EClient.__init__(self, self)
        self.openPositions={}


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


    def position(self, account: str, contract: Contract, position: float,avgCost: float):
        super().position(account, contract, position, avgCost)
        self.openPositions[contract.symbol]={"stocks":position,"cost":avgCost}
        print("Symbol:", contract.symbol,"Stocks:", position, "Avg cost:", avgCost,"Added to the list")


    def positionEnd(self):
        super().positionEnd()
        print("Open Positions updated ",len(self.openPositions)," found")

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice):
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining,
              'lastFillPrice', lastFillPrice)

    def openOrder(self, orderId, contract, order, orderState):
        print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action,
              order.orderType, order.totalQuantity, orderState.status)

    def execDetails(self, reqId, contract, execution):
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId,
              execution.orderId, execution.shares, execution.lastLiquidity)

    def tickPrice(self, reqId, tickType, price, attrib):
        if tickType==67 or tickType==66:
            print("Request:",reqId)
        if tickType == 67 :
            print('The current Buying price is: ', price)
        if tickType == 66 :
            print('The current Selling price is: ', price)

def createContract(symbol:str):
    # Create contract object
    newContract = Contract()
    newContract.symbol = symbol
    newContract.secType = 'STK'
    newContract.exchange = 'SMART'
    newContract.currency = 'USD'
    return newContract


