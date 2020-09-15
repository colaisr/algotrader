import configparser
import sched
import time
import threading
from datetime import datetime
from sys import platform

from Logic.ApiWrapper import IBapi, createContract, createTrailingStopOrder, createLMTbuyorder, createMktSellOrder
from DataBase.db import flushOpenPositionsToDB, updateOpenOrdersinDB, dropPositions, dropOpenOrders, dropLiveCandidates, \
    flushLiveCandidatestoDB, checkDB, getRatingsForAllCandidatesFromDB, updatetMarketStatisticsForCandidateFromDB
from pytz import timezone

from Research.UpdateCandidates import updatetMarketStatisticsForCandidate
from Research.tipRanksScrapper import getTipRanksRatings





class IBKRWorker():
    def __init__(self):
        self.app=IBapi()
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.PORT = config['Connection']['portp']
        self.ACCOUNT = config['Account']['accp']
        self.INTERVAL = config['Connection']['interval']

        self.MACPATHTOWEBDRIVER = config['Connection']['macPathToWebdriver']
        if platform == "linux" or platform == "linux2":
            self.PATHTOWEBDRIVER = config['Connection']['macPathToWebdriver']
        elif platform == "darwin":  # mac os
            self.PATHTOWEBDRIVER = config['Connection']['macPathToWebdriver']
        elif platform == "win32":
            self.PATHTOWEBDRIVER = config['Connection']['winPathToWebdriver']
        # alg
        self.PROFIT = config['Algo']['gainP']
        self.LOSS = config['Algo']['lossP']
        self.TRAIL = config['Algo']['trailstepP']
        self.BULCKAMOUNT = config['Algo']['bulkAmountUSD']
        self.TRANDINGSTOCKS = ["AAPL", "FB", "ZG", "MSFT", "NVDA", "TSLA", "BEP", "GOOGL", "ETSY", "IVAC"]
        # debug
        self.REUSECANDIDATESFROMDB = config['Debug']['reuseCandidatesFromDb']
        self.WORKERCOUNTER = 0
        self.s = sched.scheduler(time.time, time.sleep)

    def _runMainLoop(self):
        print("Starting Todays session:", time.ctime())
        # check if DB is missing- if yes- create
        checkDB()
        self.app.connect('127.0.0.1', int(self.PORT), 123)
        self.app.nextorderId = None
        # Start the socket in a thread
        api_thread = threading.Thread(target=self.run_loop, daemon=True)
        api_thread.start()
        # Check if the API is connected via orderid
        while True:
            if isinstance(self.app.nextorderId, int):
                print('connected')
                break
            else:
                print('waiting for connection')
                time.sleep(1)
        # General Account info:
        self.start_tracking_current_PnL()
        # start tracking liquidity
        self.start_tracking_excess_liquidity()
        # start tracking open positions
        self.update_open_positions()
        # start tracking candidates
        self.start_tracking_live_candidates()
        print("**********************Connected, Ready!!! starting Worker********************")
        # starting worker in loop...
        self.s.enter(2, 1, self.workerGo, (self.s,))
        self.s.run()


    def addYahooStatisticsForCandidates(self):
        for s in self.TRANDINGSTOCKS:
            if self.REUSECANDIDATESFROMDB == 'True':
                drop, change=updatetMarketStatisticsForCandidateFromDB(s)
            else:
                drop, change = updatetMarketStatisticsForCandidate(s)
            for k,v in self.app.candidatesLive.items():
                if v["Stock"]==s:
                    self.app.candidatesLive[k]["averagePriceDropP"]=drop
                    self.app.candidatesLive[k]["averagePriceSpreadP"] = change


    def addTipRanksToCandidates(self):
        if self.REUSECANDIDATESFROMDB=='True':
            data=getRatingsForAllCandidatesFromDB()
        else:
            data=getTipRanksRatings(self.TRANDINGSTOCKS, self.PATHTOWEBDRIVER)
        for s in self.TRANDINGSTOCKS:
            for k,v in self.app.candidatesLive.items():
                v["tipranksRank"]=data[v["Stock"]]


    def start_tracking_live_candidates(self):
        # starting querry
        for s in self.TRANDINGSTOCKS:
            id = self.app.nextorderId
            print("starting to track: ", s, "traking with Id:", id)
            c = createContract(s)
            self.app.candidatesLive[id] = {"Stock": s,
                                  "Close": "-",
                                  "Open": "-",
                                  "Bid": "-",
                                  "Ask": "-",
                                  "LastPrice": "-",
                                  "averagePriceDropP": "-",
                                  "averagePriceSpreadP": "-",
                                  "tipranksRank": "-",
                                  "LastUpdate": "-"}
            self.app.reqMarketDataType(1)
            self.app.reqMktData(id, c, '', False, False, [])
            self.app.nextorderId += 1
            time.sleep(2)

        #updateYahooStatistics
        self.addYahooStatisticsForCandidates()

        # update TipranksData
        self.addTipRanksToCandidates()

        self.updateCandidatesInDB()

        print("Updated ",len(self.app.candidatesLive)," data in DB")


    def processProfits(self):
        print("Processing profits")
        for s, p in self.app.openPositions.items():
            print("Checking ",s)
            profit = p["UnrealizedPnL"] / p["Value"] * 100
            if profit > float(self.PROFIT):
                orders = self.app.openOrders
                if s in orders:
                    print("Order for ", s, "already exist- skipping")
                else:
                    print("Profit for: ", s, " is ", profit, "Creating a trailing Stop Order")
                    contract = createContract(s)
                    order = createTrailingStopOrder(p["stocks"], self.TRAIL)
                    self.app.placeOrder(self.app.nextorderId, contract, order)
                    self.app.nextorderId = self.app.nextorderId + 1
                    print("Created a Trailing Stop order for ", s, " at level of ", self.TRAIL, "%")
            elif profit <float(self.LOSS):
                orders = self.app.openOrders
                if s in orders:
                    print("Order for ", s, "already exist- skipping")
                else:
                    print("loss for: ", s, " is ", profit, "Creating a Market Sell Order")
                    contract = createContract(s)
                    order = createMktSellOrder(p['stocks'])
                    self.app.placeOrder(self.app.nextorderId, contract, order)
                    self.app.nextorderId = self.app.nextorderId + 1
                    print("Created a Market Sell order for ", s)



    def evaluateBuy(self,s):
        print("evaluating ",s,"for a Buy")

        for c in self.app.candidatesLive.values():
            if c["Stock"]==s:
                ask_price=c["Ask"]
                last_closing=c["Close"]
                last_open=c["Open"]
                last_price=c["LastPrice"]
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
            self.buyTheStock(ask_price, s)
        else:
            print("The price of :",ask_price,"was not in range of :",average_daily_dropP, " % "," Or the Rating of ",tipRank," was not good enough")

        pass


    def buyTheStock(self,ask_price, s):
        contract = createContract(s)
        stocksToBuy=int(int(self.BULCKAMOUNT)/ask_price)
        if stocksToBuy>0:
            print("Issued the BUY order at ", ask_price,"for ",stocksToBuy," Stocks of ",s)
            order = createLMTbuyorder(stocksToBuy, ask_price)
            self.app.placeOrder(self.app.nextorderId, contract, order)
            self.app.nextorderId = self.app.nextorderId + 1
        else:
            print("The single stock is too expensive - skipping")


    def processCandidates(self):

        excessLiquidity=self.app.excessLiquidity
        if float(excessLiquidity)<1000:
            return
        else:
            print("The Excess liquidity is :",excessLiquidity," searching candidates")
            res = sorted(self.app.candidatesLive.items(), key=lambda x: x[1]['tipranksRank'],reverse=True)
            for i,c in res:
                if c['Stock'] in self.app.openPositions:
                    continue
                else:
                    self.evaluateBuy(c['Stock'])

    def workerGo(self,sc):
        est = timezone('EST')
        fmt = '%Y-%m-%d %H:%M:%S'
        local_time=datetime.now().strftime(fmt)
        est_time = datetime.now(est).strftime(fmt)

        print("-------Processing Worker...---Local Time",local_time,"----EST Time: ", est_time, "--------------------")
        # collect and update
        self.requestOrders()
        self.update_open_positions()
        self.updateCandidatesInDB()

        # print("Open positions:")
        # pprint.pprint(app.openPositions)
        # print("Tracked Candidates:")
        # pprint.pprint(app.candidatesLive)

        # process
        self.processCandidates()
        self.processProfits()
        print("...............Worker finished.........................")

        self.s.enter(float(self.INTERVAL), 1, self.workerGo, (sc,))


    def run_loop(self):
        self.app.run()


    def updateOpenPositionsInDB(self):
        dropPositions()
        flushOpenPositionsToDB(self.app.openPositions)
        print(len(self.app.openPositionsLiveDataRequests), " open positions info updated in DB")

    def updateCandidatesInDB(self):
        dropLiveCandidates()
        flushLiveCandidatestoDB(self.app.candidatesLive)
        print(len(self.app.candidatesLive), " Candidates updated in DB")


    def updateOpenOrdersInDB(self):
        dropOpenOrders()
        updateOpenOrdersinDB(self.app.openOrders)

    def update_open_positions(self):
        # update positions from IBKR
        print("Updating positions:")
        self.app.openPositionsLiveDataRequests={} #reset requests dictionary
        self.app.reqPositions()  # requesting open positions
        time.sleep(1)
        for s, p in self.app.openPositions.items():  # start tracking one by one
            if s not in self.app.openPositionsLiveDataRequests.values():
                id = self.app.nextorderId
                p["tracking_id"]=id
                self.app.openPositionsLiveDataRequests[id] = s
                self.app.reqPnLSingle(id, self.ACCOUNT, "", p["conId"])
                self.app.nextorderId += 1
        time.sleep(2)
        self.updateOpenPositionsInDB()


    def requestOrders(self):
        print("Updating all open Orders")
        self.app.openOrders = {}
        self.app.reqAllOpenOrders()
        time.sleep(1)
        self.updateOpenOrdersInDB()

        print(len(self.app.openOrders), " Orders found and saved to DB")


    def start_tracking_excess_liquidity(self):
        id = self.app.nextorderId
        self.app.reqAccountSummary(id, "All", "ExcessLiquidity")
        self.app.nextorderId += 1
        time.sleep(0.5)


    def start_tracking_current_PnL(self):
        global id, status
        id = self.app.nextorderId
        self.app.reqPnL(id, self.ACCOUNT, "")
        time.sleep(0.5)
        self.app.nextorderId = self.app.nextorderId + 1
        print(self.app.generalStatus)




if __name__ == '__main__':
    w=IBKRWorker()
    w._runMainLoop()
    i=2
