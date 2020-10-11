import time
import threading
from datetime import datetime
from Logic.ApiWrapper import IBapi, createContract, createTrailingStopOrder, create_limit_buy_order, createMktSellOrder
from pytz import timezone
from Research.UpdateCandidates import get_yahoo_stats_for_candidate
from Research.tipRanksScrapper import get_tiprank_ratings_to_Stocks


class IBKRWorker():
    def __init__(self, settings):
        self.app = IBapi()
        self.settings = settings


    def connect_and_prepare(self):
        """
Connecting to IBKR API and initiating the connection instance
        :return:
        """
        self.connect_to_tws()
        self.start_tracking_excess_liquidity()
        # start tracking open positions
        self.update_open_positions()
        # start tracking candidates
        self.evaluate_and_track_candidates()
        self.update_target_price_for_tracked_stocks()
        print("Connected to IBKR and READY")
        return "Successfully Connected"

    def connect_to_tws(self):
        """
Creates the connection - starts listner for events
        """
        print("Starting connection to IBKR")
        self.app.connect('127.0.0.1', int(self.settings.PORT), 123)
        self.app.nextorderId = None
        # Start the socket in a thread
        api_thread = threading.Thread(target=self.run_loop, daemon=True)
        api_thread.start()
        # Check if the API is connected via orderid
        while True:
            if isinstance(self.app.nextorderId, int):
                print('Successfully connected to API')
                break
            else:
                print('Waiting for connection...')
                time.sleep(1)
        # General Account info:
        # self.request_current_PnL()
        # start tracking liquidity

    def add_yahoo_stats_to_live_candidates(self):
        """
gets a Yahoo statistics to all tracked candidates and adds it to them
        """
        for k, v in self.app.candidatesLive.items():
            print("Getting Yahoo market data for ", v['Stock'])
            drop, change = get_yahoo_stats_for_candidate(v['Stock'])
            self.app.candidatesLive[k]["averagePriceDropP"] = drop
            self.app.candidatesLive[k]["averagePriceSpreadP"] = change
            print("Yahoo market data for ", v['Stock'], " shows average ", drop, "% drop")

    def add_ratings_to_liveCandidates(self):
        """
getting and updating tiprank rank for live candidates
        """
        print("Getting ranks for :", self.settings.TRANDINGSTOCKS)
        ranks = get_tiprank_ratings_to_Stocks(self.settings.TRANDINGSTOCKS, self.settings.PATHTOWEBDRIVER)
        for k, v in self.app.candidatesLive.items():
            v["tipranksRank"] = ranks[v["Stock"]]
            print("Updated ", v["tipranksRank"], " rank for ", v["Stock"])

    def evaluate_and_track_candidates(self):
        """
Starts tracking the Candidates and adds the statistics
        """
        print("Starting to track ", len(self.settings.TRANDINGSTOCKS), " Candidates")
        # starting querry
        trackedStockN = 1
        for s in self.settings.TRANDINGSTOCKS:
            id = self.app.nextorderId
            print("starting to track: ", trackedStockN, " of ", len(self.settings.TRANDINGSTOCKS), " ", s,
                  "traking with Id:",
                  id)
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
            lastID = id
            self.app.nextorderId += 1
            trackedStockN += 1
        time.sleep(1)
        # while self.app.candidatesLive[lastID]["LastPrice"] == '-':
        #     time.sleep(1)
        #     print("Waiting for last Stock market data to receive")

        # updateYahooStatistics
        self.add_yahoo_stats_to_live_candidates()

        # update TipranksData
        self.add_ratings_to_liveCandidates()

        print(len(self.app.candidatesLive), " Candidates evaluated and started to track")

    def process_positions(self):
        """
Processes the positions to identify Profit/Loss
        """
        print("Processing profits")
        for s, p in self.app.openPositions.items():
            profit = p["UnrealizedPnL"] / p["Value"] * 100
            print("The profit for ", s, " is ", profit, " %")
            if profit > float(self.settings.PROFIT):
                orders = self.app.openOrders
                if s in orders:
                    print("Order for ", s, "already exist- skipping")
                else:
                    print("Profit for: ", s, " is ", profit, "Creating a trailing Stop Order to take a Profit")
                    contract = createContract(s)
                    order = createTrailingStopOrder(p["stocks"], self.settings.TRAIL)
                    self.app.placeOrder(self.app.nextorderId, contract, order)
                    self.app.nextorderId = self.app.nextorderId + 1
                    print("Created a Trailing Stop order for ", s, " at level of ", self.settings.TRAIL, "%")
                    self.log_decision("profits.txt",
                                      "Created a Trailing Stop order for " + s + " at level of " + self.settings.TRAIL + "%")
            elif profit < float(self.settings.LOSS):
                orders = self.app.openOrders
                if s in orders:
                    print("Order for ", s, "already exist- skipping")
                else:
                    print("loss for: ", s, " is ", profit, "Creating a Market Sell Order to minimize the Loss")
                    contract = createContract(s)
                    order = createMktSellOrder(p['stocks'])
                    self.app.placeOrder(self.app.nextorderId, contract, order)
                    self.app.nextorderId = self.app.nextorderId + 1
                    print("Created a Market Sell order for ", s)
                    self.log_decision("loses.txt", "Created a Market Sell order for " + s)

    def evaluate_stock_for_buy(self, s):
        """
Evaluates stock for buying
        :param s:
        """
        print("Evaluating ", s, "for a Buy")
        # finding stock in Candidates
        for c in self.app.candidatesLive.values():
            if c["Stock"] == s:
                ask_price = c["Ask"]
                average_daily_dropP = c["averagePriceDropP"]
                tipRank = c["tipranksRank"]
                target_price = c["target_price"]
                break

        if ask_price == -1:  # market is closed
            print('The market is closed skipping...')
        elif ask_price < target_price and float(tipRank) > 8:
            self.buy_the_stock(ask_price, s)
        else:
            print("The price of :", ask_price, "was not in range of :", average_daily_dropP, " % ",
                  " Or the Rating of ", tipRank, " was not good enough")

        pass

    def update_target_price_for_tracked_stocks(self):
        """
Update target price for all tracked stocks
        :return:
        """
        print("Updating target prices for Candidates")
        for c in self.app.candidatesLive.values():
            print("Updating target price for ", c["Stock"])
            ask_price = c["Ask"]
            close = c["Close"]
            open = c["Open"]
            last = c["LastPrice"]
            average_daily_dropP = c["averagePriceDropP"]
            tipRank = c["tipranksRank"]
            print("Close:", c["Close"])
            print("Open:", c["Open"])
            print("LastPrice:", c["LastPrice"])

            if open != '-':  # market is closed
                c["target_price"] = open - open / 100 * average_daily_dropP
                print("Target price for ", c["Stock"], " updated to ", c["target_price"], " based on Open price")
            elif close != '-':  # market is open
                c["target_price"] = close - close / 100 * average_daily_dropP
                print("Target price for ", c["Stock"], " updated to ", c["target_price"], " based on Close price")
            else:
                c["target_price"] = last - last / 100 * average_daily_dropP
                print("Target price for ", c["Stock"], " updated to ", c["target_price"], " based on last price")

    def buy_the_stock(self, price, s):
        """
Creates order to buy a stock at specific price
        :param price: price to buy at limit
        :param s: Stocks to buy
        """
        contract = createContract(s)
        stocksToBuy = int(int(self.settings.BULCKAMOUNT) / price)
        if stocksToBuy > 0:
            order = create_limit_buy_order(stocksToBuy, price)
            self.app.placeOrder(self.app.nextorderId, contract, order)
            self.app.nextorderId = self.app.nextorderId + 1
            print("Issued the BUY order at ", price, "for ", stocksToBuy, " Stocks of ", s)
            self.log_decision("buys.txt", "Issued the BUY order at " + price + "for " + stocksToBuy + " Stocks of " + s)
        else:
            print("The single stock is too expensive - skipping")

    def process_candidates(self):
        """
processes candidates for buying
        :return:
        """
        excessLiquidity = self.app.excessLiquidity
        if float(excessLiquidity) < 1000:
            print("Excess liquidity is ", excessLiquidity, " it is less than 1000 - skipping buy")
            return
        else:
            print("The Excess liquidity is :", excessLiquidity, " searching candidates")
            # updating the targets if market was open in the middle
            self.update_target_price_for_tracked_stocks()
            res = sorted(self.app.candidatesLive.items(), key=lambda x: x[1]['tipranksRank'], reverse=True)
            print(len(res), "Candidates found,sorted by Tipranks ranks")
            for i, c in res:
                if c['Stock'] in self.app.openPositions:
                    print("Skipping ", c['Stock'], " as it is in open positions.")
                    continue
                else:
                    self.evaluate_stock_for_buy(c['Stock'])

    def process_positions_candidates(self):
        """
Process Open positions and Candidates
        """
        est = timezone('EST')
        fmt = '%Y-%m-%d %H:%M:%S'
        local_time = datetime.now().strftime(fmt)
        est_time = datetime.now(est).strftime(fmt)

        print("-------Starting Worker..", "----EST Time: ", est_time, "--------------------")

        print("Checking connection")
        conState = self.app.isConnected()
        if conState:
            print("Connection is fine- proceeding")
        else:
            print("Connection lost-reconnecting")
            self.connect_to_tws()

        # collect and update
        self.update_open_orders()
        self.update_open_positions()

        # process
        self.process_candidates()
        self.process_positions()
        print("...............Worker finished.........................")
        return "Last worker execution" + local_time

    def run_loop(self):
        self.app.run()

    def update_open_positions(self):
        """
updating all openPositions
        """
        # update positions from IBKR
        print("Updating open Positions:")
        self.app.openPositionsLiveDataRequests = {}  # reset requests dictionary
        self.app.reqPositions()  # requesting open positions
        time.sleep(1)
        lastId = 0
        for s, p in self.app.openPositions.items():  # start tracking one by one
            if s not in self.app.openPositionsLiveDataRequests.values():
                id = self.app.nextorderId
                p["tracking_id"] = id
                self.app.openPositionsLiveDataRequests[id] = s
                self.app.reqPnLSingle(id, self.settings.ACCOUNT, "", p["conId"])
                print("Started tracking ", s, " position PnL")
                lastId = s
                self.app.nextorderId += 1

        time.sleep(3)
        print(len(self.app.openPositions), " open positions updated")

    def update_open_orders(self):
        """
Requests all open orders
        """
        print("Updating all open orders")
        self.app.openOrders = {}
        self.app.reqAllOpenOrders()
        time.sleep(1)

        print(len(self.app.openOrders), " open orders found ")

    def start_tracking_excess_liquidity(self):
        """
Start tracking excess liquidity - the value is updated every 3 minutes
        """
        # todo: add safety to not buy faster than every 3 minutes
        id = self.app.nextorderId
        self.app.reqAccountSummary(id, "All", "ExcessLiquidity")
        self.app.nextorderId += 1
        time.sleep(0.5)

    def request_current_PnL(self):
        """
Creating a PnL request the result will be stored in generalStarus
        """
        global id, status
        id = self.app.nextorderId
        print("Requesting Daily PnL")
        self.app.reqPnL(id, self.settings.ACCOUNT, "")
        time.sleep(0.5)
        self.app.nextorderId = self.app.nextorderId + 1
        print(self.app.generalStatus)

    def log_decision(self, logFile, order):
        with open(logFile, "a") as f:
            currentDt = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            order = currentDt + '---' + order
            f.write(order)
