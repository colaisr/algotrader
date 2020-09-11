import configparser
import sched
import time
import threading
from datetime import datetime
from sys import platform
import pprint

from ApiWrapper import IBapi, createContract, createTrailingStopOrder, createLMTbuyorder, createMktSellOrder
from DataBase.db import flushOpenPositionsToDB, updateOpenOrdersinDB, dropPositions, dropOpenOrders, dropLiveCandidates, \
    flushLiveCandidatestoDB, checkDB, getRatingsForAllCandidatesFromDB, updatetMarketStatisticsForCandidateFromDB
from pytz import timezone

from Research.UpdateCandidates import updatetMarketStatisticsForCandidate
from Research.tipRanksScrapper import getTipRanksRatings

config = configparser.ConfigParser()
config.read('config.ini')
PORT = config['Connection']['portp']
ACCOUNT = config['Account']['accp']
INTERVAL = config['Connection']['interval']

MACPATHTOWEBDRIVER = config['Connection']['macPathToWebdriver']
if platform == "linux" or platform == "linux2":
    PATHTOWEBDRIVER = config['Connection']['macPathToWebdriver']
elif platform == "darwin":#mac os
    PATHTOWEBDRIVER = config['Connection']['macPathToWebdriver']
elif platform == "win32":
    PATHTOWEBDRIVER = config['Connection']['winPathToWebdriver']
# alg
PROFIT = config['Algo']['gainP']
LOSS = config['Algo']['lossP']
TRAIL = config['Algo']['trailstepP']
BULCKAMOUNT = config['Algo']['bulkAmountUSD']
TRANDINGSTOCKS = ["AAPL", "FB", "ZG", "MSFT", "NVDA", "TSLA", "BEP", "GOOGL","ETSY"]
#debug
REUSECANDIDATESFROMDB = config['Debug']['reuseCandidatesFromDb']
WORKERCOUNTER=0

def addYahooStatisticsForCandidates():
    for s in TRANDINGSTOCKS:
        if REUSECANDIDATESFROMDB == 'True':
            drop, change=updatetMarketStatisticsForCandidateFromDB(s)
        else:
            drop, change = updatetMarketStatisticsForCandidate(s)
        for k,v in app.candidatesLive.items():
            if v["Stock"]==s:
                app.candidatesLive[k]["averagePriceDropP"]=drop
                app.candidatesLive[k]["averagePriceSpreadP"] = change


def addTipRanksToCandidates():
    if REUSECANDIDATESFROMDB=='True':
        data=getRatingsForAllCandidatesFromDB()
    else:
        data=getTipRanksRatings(TRANDINGSTOCKS, PATHTOWEBDRIVER)
    for s in TRANDINGSTOCKS:
        for k,v in app.candidatesLive.items():
            v["tipranksRank"]=data[v["Stock"]]


def start_tracking_live_candidates():
    # starting querry
    for s in TRANDINGSTOCKS:
        id = app.nextorderId
        print("starting to track: ", s, "traking with Id:", id)
        c = createContract(s)
        app.candidatesLive[id] = {"Stock": s,
                              "Close": "-",
                              "Open": "-",
                              "Bid": "-",
                              "Ask": "-",
                              "LastPrice": "-",
                              "averagePriceDropP": "-",
                              "averagePriceSpreadP": "-",
                              "tipranksRank": "-",
                              "LastUpdate": "-"}
        app.reqMarketDataType(1)
        app.reqMktData(id, c, '', False, False, [])
        app.nextorderId += 1
        time.sleep(2)

    #updateYahooStatistics
    addYahooStatisticsForCandidates()

    # update TipranksData
    addTipRanksToCandidates()

    updateCandidatesInDB()

    print("Updated ",len(app.candidatesLive)," data in DB")


def processProfits():
    print("Processing profits")
    for s, p in app.openPositions.items():
        print("Checking ",s)
        profit = p["UnrealizedPnL"] / p["Value"] * 100
        if profit > float(PROFIT):
            orders = app.openOrders
            if s in orders:
                print("Order for ", s, "already exist- skipping")
            else:
                print("Profit for: ", s, " is ", profit, "Creating a trailing Stop Order")
                contract = createContract(s)
                order = createTrailingStopOrder(p["stocks"], TRAIL)
                app.placeOrder(app.nextorderId, contract, order)
                app.nextorderId = app.nextorderId + 1
                print("Created a Trailing Stop order for ", s, " at level of ", TRAIL, "%")
        elif profit <float(LOSS):
            orders = app.openOrders
            if s in orders:
                print("Order for ", s, "already exist- skipping")
            else:
                print("loss for: ", s, " is ", profit, "Creating a Market Sell Order")
                contract = createContract(s)
                order = createMktSellOrder(p['stocks'])
                app.placeOrder(app.nextorderId, contract, order)
                app.nextorderId = app.nextorderId + 1
                print("Created a Market Sell order for ", s)



def evaluateBuy(s):
    print("evaluating ",s,"for a Buy")

    for c in app.candidatesLive.values():
        if c["Stock"]==s:
            ask_price=c["Ask"]
            last_closing=c["Close"]
            last_open=c["Open"]
            last_price=c["lastPrice"]
            average_daily_dropP=c["averagePriceDropP"]
            tipRank = c["tipranksRank"]

            break

    if last_open != '-':  # market is closed
        target_price=last_open-last_open/100*average_daily_dropP
    elif last_closing !='-':                #market is open
        target_price = last_closing - last_closing / 100 * average_daily_dropP
    else:
        target_price = last_price - last_price / 100 * average_daily_dropP

    if ask_price==-1:#market is closed
        print('The market is closed skipping...')
    elif ask_price<target_price and float(tipRank)>8:
        buyTheStock(ask_price, s)
    else:
        print("The price of :",ask_price,"was not in range of :",average_daily_dropP, " % "," Or the Rating of ",tipRank," was not good enough")

    pass


def buyTheStock(ask_price, s):
    contract = createContract(s)
    stocksToBuy=int(int(BULCKAMOUNT)/ask_price)
    if stocksToBuy>0:
        print("Issued the BUY order at ", ask_price,"for ",stocksToBuy," Stocks of ",s)
        order = createLMTbuyorder(stocksToBuy, ask_price)
        app.placeOrder(app.nextorderId, contract, order)
        app.nextorderId = app.nextorderId + 1
    else:
        print("The single stock is too expensive - skipping")


def processCandidates():

    excessLiquidity=app.excessLiquidity
    if float(excessLiquidity)<1000:
        return
    else:
        print("The Excess liquidity is :",excessLiquidity," searching candidates")
        for s in TRANDINGSTOCKS:
            if s in app.openPositions:
                continue
            else:
                evaluateBuy(s)


s = sched.scheduler(time.time, time.sleep)


def workerGo(sc):
    est = timezone('EST')
    fmt = '%Y-%m-%d %H:%M:%S'
    local_time=datetime.now().strftime(fmt)
    est_time = datetime.now(est).strftime(fmt)

    print("-------Processing Worker...---Local Time",local_time,"----EST Time: ", time, "--------------------")
    # collect and update
    requestOrders()
    update_open_positions()
    updateCandidatesInDB()

    # print("Open positions:")
    # pprint.pprint(app.openPositions)
    # print("Tracked Candidates:")
    # pprint.pprint(app.candidatesLive)

    # process
    processCandidates()
    processProfits()
    print("...............Worker finished.........................")

    s.enter(float(INTERVAL), 1, workerGo, (sc,))


def run_loop():
    app.run()


def updateOpenPositionsInDB():
    dropPositions()
    flushOpenPositionsToDB(app.openPositions)
    print(len(app.openPositionsLiveDataRequests), " open positions info updated in DB")

def updateCandidatesInDB():
    dropLiveCandidates()
    flushLiveCandidatestoDB(app.candidatesLive)
    print(len(app.candidatesLive), " Candidates updated in DB")


def updateOpenOrdersInDB():
    dropOpenOrders()
    updateOpenOrdersinDB(app.openOrders)

def update_open_positions():
    # update positions from IBKR
    print("Updating positions:")
    app.openPositionsLiveDataRequests={} #reset requests dictionary
    app.reqPositions()  # requesting open positions
    time.sleep(1)
    for s, p in app.openPositions.items():  # start tracking one by one
        if s not in app.openPositionsLiveDataRequests.values():
            id = app.nextorderId
            p["tracking_id"]=id
            app.openPositionsLiveDataRequests[id] = s
            app.reqPnLSingle(id, ACCOUNT, "", p["conId"])
            app.nextorderId += 1
    time.sleep(2)
    updateOpenPositionsInDB()


def requestOrders():
    print("Updating all open Orders")
    app.openOrders = {}
    app.reqAllOpenOrders()
    time.sleep(1)
    updateOpenOrdersInDB()

    print(len(app.openOrders), " Orders found and saved to DB")


def start_tracking_excess_liquidity():
    id = app.nextorderId
    app.reqAccountSummary(id, "All", "ExcessLiquidity")
    app.nextorderId += 1
    time.sleep(0.5)


def start_tracking_current_PnL():
    global id, status
    id = app.nextorderId
    app.reqPnL(id, ACCOUNT, "")
    time.sleep(0.5)
    app.nextorderId = app.nextorderId + 1
    print(app.generalStatus)


def mainMethod():
    global app
    print("Starting Todays session:", time.ctime())
    # check if DB is missing- if yes- create
    checkDB()
    app = IBapi()
    app.connect('127.0.0.1', int(PORT), 123)
    app.nextorderId = None
    # Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()
    # Check if the API is connected via orderid
    while True:
        if isinstance(app.nextorderId, int):
            print('connected')
            break
        else:
            print('waiting for connection')
            time.sleep(1)
    # General Account info:
    start_tracking_current_PnL()
    # start tracking liquidity
    start_tracking_excess_liquidity()
    # start tracking open positions
    update_open_positions()
    # start tracking candidates
    start_tracking_live_candidates()
    print("**********************Connected, Ready!!! starting Worker********************")
    # starting worker in loop...
    s.enter(2, 1, workerGo, (s,))
    s.run()


if __name__ == '__main__':
    mainMethod()
