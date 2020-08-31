from ibapi.common import MarketDataTypeEnum
from twsapi.ibapi.contract import Contract
from twsapi.ibapi.order import Order
from twsapi.ibapi.client import EClient
from twsapi.ibapi.wrapper import EWrapper
import time
import threading


def error_handler(msg):
    """Handles the capturing of error messages"""
    print("Server Error: %s" % msg)


def reply_handler(msg):
    """Handles of server replies"""
    print("Server Response: %s, %s" % (msg.typeName, msg))


def create_contract(symbol, sec_type, exch, prim_exch, curr):
    """Create a Contract object defining what will
    be purchased, at which exchange and in which currency.

    symbol - The ticker symbol for the contract
    sec_type - The security type for the contract ('STK' is 'stock')
    exch - The exchange to carry out the contract on
    prim_exch - The primary exchange to carry out the contract on
    curr - The currency in which to purchase the contract"""
    contract = Contract()
    contract.m_symbol = symbol
    contract.m_secType = sec_type
    contract.m_exchange = exch
    contract.m_primaryExch = prim_exch
    contract.m_currency = curr
    return contract


def create_order(order_type, quantity, action):
    """Create an Order object (Market/Limit) to go long/short.

    order_type - 'MKT', 'LMT' for Market or Limit orders
    quantity - Integral number of assets to order
    action - 'BUY' or 'SELL'"""
    order = Order()
    order.m_orderType = order_type
    order.m_totalQuantity = quantity
    order.m_action = action
    return order


class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)

    def contractDetailsEnd(self, reqId: int):

        super().contractDetailsEnd(reqId)

        print("ContractDetailsEnd. ReqId:", reqId)

    def tickPrice(self, reqId, tickType, price, attrib):
        if tickType == 67 :
            print('The current Buying price is: ', price)
        if tickType == 66 :
            print('The current Selling price is: ', price)


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



    def position(self, account: str, contract: Contract, position: float,avgCost: float):

        super().position(account, contract, position, avgCost)
        print("Position.", "Account:", account, "Symbol:", contract.symbol, "SecType:",
        contract.secType, "Currency:", contract.currency,
        "Position:", position, "Avg cost:", avgCost)


def run_loop():
    app.run()


app = IBapi()
app.connect('127.0.0.1', 7496, 123)
app.nextorderId = None


# Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()
print("Started waiting for connection")
# Check if the API is connected via orderid
while True:
    if isinstance(app.nextorderId, int):
        print('connected')
        break
    else:
        print('waiting for connection')
        time.sleep(1)

# # Create contract object
# apple_contract = Contract()
# apple_contract.symbol = 'FB'
# apple_contract.secType = 'STK'
# apple_contract.exchange = 'SMART'
# apple_contract.currency = 'USD'
#
# # Create order object
# order = Order()
# order.action = 'BUY'
# order.totalQuantity = 2
# order.lmtPrice=100
# order.orderType = 'LMT'

#getting the data for the stock
# print("request for market data APL")
# app.reqMarketDataType(MarketDataTypeEnum.DELAYED)
# app.reqMktData(1, apple_contract, '', False, False, [])

# Place order
# app.placeOrder(app.nextorderId, apple_contract, order)
# app.nextorderId += 1




# #Getting managed Accounts:
# print("The related accounts:",app.reqManagedAccts())

#get all the positions
print("Getting all open positions:")
app.reqPositions()

# print("Get all open Orders")
# app.reqAllOpenOrders()


time.sleep(20)



app.disconnect()
