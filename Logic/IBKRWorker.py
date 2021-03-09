import time
import threading
from datetime import datetime, timedelta

from Logic.ApiWrapper import IBapi, createContract, createTrailingStopOrder, create_limit_buy_order, createMktSellOrder
from pytz import timezone


class IBKRWorker():
    def __init__(self, settings):
        self.app = IBapi()
        self.settings = settings
        self.app.setting = self.settings
        self.stocks_data_from_server = []
        self.last_worker_execution_time=None

    def prepare_and_connect(self, status_callback, notification_callback):
        """
Connecting to IBKR API and initiating the connection instance
        :return:
        """
        status_callback.emit("Connecting")
        try:
            notification_callback.emit("Begin prepare and connect")
            # self.get_market_data_from_server(notification_callback)
            self.connect_to_tws(notification_callback)
            # self.check_if_holiday(notification_callback)
            self.request_current_PnL(notification_callback)
            self.start_tracking_excess_liquidity(notification_callback)
            # start tracking open positions
            self.update_open_positions(notification_callback)

            # request open orders
            self.update_open_orders(notification_callback)
            # start tracking candidates
            self.evaluate_and_track_candidates(notification_callback)
            self.update_target_price_for_tracked_stocks(notification_callback)
            notification_callback.emit("Connected to IBKR and READY")
            status_callback.emit("Connected and ready")
        except Exception as e:
            if hasattr(e, 'message'):
                notification_callback.emit("Error in connection and preparation : " + str(e.message))
            else:
                notification_callback.emit("Error in connection and preparation : " + str(e))

    def connect_to_tws(self, notification_callback):
        """
Creates the connection - starts listner for events
        """

        self.app.nextorderId = None
        while not isinstance(self.app.nextorderId, int):
            retries = 0
            notification_callback.emit("Restarting connection to IBKR")
            self.app.connect('127.0.0.1', int(self.settings.PORT), 123)

            # Start the socket in a thread
            api_thread = threading.Thread(target=self.run_loop, name='ibkrConnection', daemon=True)
            api_thread.start()
            # Check if the API is connected via orderid

            while True:
                if isinstance(self.app.nextorderId, int):
                    notification_callback.emit('Successfully connected to API')
                    break
                else:
                    notification_callback.emit('Waiting for connection...attempt:' + str(retries))
                    time.sleep(1)
                    retries = retries + 1
                    if retries > 10:
                        break

    def evaluate_and_track_candidates(self, notification_callback=None):
        """
Starts tracking the Candidates and adds the statistics
        """
        time.sleep(1)
        stock_names = [o.ticker for o in self.settings.CANDIDATES]
        notification_callback.emit("Starting to track " + ','.join(stock_names) + " Candidates")
        # starting querry
        trackedStockN = 1
        for s in self.settings.CANDIDATES:
            id = self.app.nextorderId
            notification_callback.emit(
                "starting to track: " + str(trackedStockN) + " of " + str(
                    len(self.settings.CANDIDATES)) + " " + s.ticker +
                " traking with Id:" +
                str(id))
            c = createContract(s.ticker)
            self.app.candidatesLive[id] = {"Stock": s.ticker,
                                           "Close": "-",
                                           "Open": "-",
                                           "Bid": "-",
                                           "Ask": "-",
                                           "averagePriceDropP": "-",
                                           "averagePriceSpreadP": "-",
                                           "tipranksRank": "-",
                                           "LastUpdate": "-"}
            self.app.reqMarketDataType(1)
            self.app.reqMktData(id, c, '', False, False, [])
            self.app.nextorderId += 1
            trackedStockN += 1

        have_empty = True
        counter = 0
        while have_empty:
            time.sleep(1)
            notification_callback.emit("Waiting for last requested candidate Close price :" + str(counter))
            closings = [str(x['Close']) for x in self.app.candidatesLive.values()]
            if '-' in closings:
                have_empty = True
            else:
                have_empty = False
            counter += 1


        self.add_market_data_to_live_candidates(notification_callback)

        notification_callback.emit(str(len(self.app.candidatesLive)) + " Candidates evaluated and started to track")

    def process_positions(self, notification_callback=None):
        """
Processes the positions to identify Profit/Loss
        """
        notification_callback.emit("Processing profits")

        for s, p in self.app.openPositions.items():
            if 'Value' in p.keys():
                if p["Value"] != 0:
                    notification_callback.emit("Processing " + s)
                    profit = p["UnrealizedPnL"] / p["Value"] * 100
                    notification_callback.emit("The profit for " + s + " is " + str(profit) + " %")
                    if profit > float(self.settings.PROFIT):
                        orders = self.app.openOrders
                        if s in orders:
                            notification_callback.emit("Order for " + s + "already exist- skipping")
                        elif int(p["stocks"]) < 0:
                            notification_callback.emit(
                                "The " + s + " is SHORT position number of stocks is negative: " + p["stocks"])
                        else:
                            notification_callback.emit("Profit for: " + s + " is " + str(profit) +
                                                       "Creating a trailing Stop Order to take a Profit")
                            contract = createContract(s)
                            order = createTrailingStopOrder(p["stocks"], self.settings.TRAIL)

                            self.app.placeOrder(self.app.nextorderId, contract, order)
                            self.app.nextorderId = self.app.nextorderId + 1
                            notification_callback.emit("Created a Trailing Stop order for " + s + " at level of " +
                                                       str(self.settings.TRAIL) + "%")
                            self.log_decision("LOG/profits.txt",
                                              "Created a Trailing Stop order for " + s + " at level of " + self.settings.TRAIL + "%"+" The profit was:"+str(profit))
                    elif profit < float(self.settings.LOSS):
                        orders = self.app.openOrders
                        if s in orders:
                            notification_callback.emit("Order for " + s + "already exist- skipping")
                        else:
                            notification_callback.emit("loss for: " + s + " is " + str(profit) +
                                                       "Creating a Market Sell Order to minimize the Loss")
                            contract = createContract(s)
                            order = createMktSellOrder(p['stocks'])
                            self.app.placeOrder(self.app.nextorderId, contract, order)
                            self.app.nextorderId = self.app.nextorderId + 1
                            notification_callback.emit("Created a Market Sell order for " + s)
                            self.log_decision("LOG/loses.txt", "Created a Market Sell order for " + s+" The profit was:"+str(profit))

                else:
                    notification_callback.emit("Position " + s + " skept its Value is 0")
            else:
                notification_callback.emit("Position " + s + " skept it has no Value")

    def evaluate_stock_for_buy(self, s, notification_callback=None):
        """
Evaluates stock for buying
        :param s:
        """
        notification_callback.emit("Evaluating " + s + "for a Buy")
        result='evaluating'
        # finding stock in Candidates
        for c in self.app.candidatesLive.values():
            if c["Stock"] == s:
                ask_price = c["Ask"]
                average_daily_dropP = c["averagePriceDropP"]
                tipRank = c["tipranksRank"]
                target_price = c["target_price"]
                break

        if ask_price == -1:  # market is closed
            notification_callback.emit('The market is closed skipping...')
            result='skept'
        elif ask_price < target_price and float(tipRank) > 8:
            self.buy_the_stock(ask_price, s, notification_callback)
            result='bought'

        else:
            notification_callback.emit(
                "The price of :" + str(ask_price) + "was not in range of :" + str(average_daily_dropP) + " % " +
                " Or the Rating of " + str(tipRank) + " was not good enough")
            result='skept'

        return result

    def update_target_price_for_tracked_stocks(self, notification_callback=None):
        """
Update target price for all tracked stocks
        :return:
        """
        notification_callback.emit("Updating target prices for Candidates")
        for c in self.app.candidatesLive.values():
            notification_callback.emit("Updating target price for " + c["Stock"])
            close = c["Close"]
            open = c["Open"]
            average_daily_dropP = c["averagePriceDropP"]

            if open != '-':  # market is closed
                c["target_price"] = open - open / 100 * average_daily_dropP
                notification_callback.emit("Target price for " + str(c["Stock"]) + " updated to " + str(
                    c["target_price"]) + " based on Open price")
            elif close != '-':  # market is open
                c["target_price"] = close - close / 100 * average_daily_dropP
                notification_callback.emit("Target price for " + str(c["Stock"]) + " updated to " + str(
                    c["target_price"]) + " based on Close price")
            else:

                c["target_price"] = 0
                notification_callback.emit("Skept target price for " + str(c["Stock"]) + "Closing price missing")
                continue

    def buy_the_stock(self, price, s, notification_callback=None):
        """
Creates order to buy a stock at specific price
        :param price: price to buy at limit
        :param s: Stocks to buy
        """
        if self.settings.ALLOWBUY==True:
            contract = createContract(s)
            stocksToBuy = int(int(self.settings.BULCKAMOUNT) / price)
            if stocksToBuy > 0:  # very important - check for available trades everywhere!!!

                order = create_limit_buy_order(stocksToBuy, price)
                self.app.placeOrder(self.app.nextorderId, contract, order)

                self.app.nextorderId = self.app.nextorderId + 1
                notification_callback.emit(
                    "Issued the BUY order at " + str(price) + "for " + str(stocksToBuy) + " Stocks of " + s)
                self.log_decision("LOG/buys.txt",
                                  "Issued the BUY order at " + str(price) + "for " + str(stocksToBuy) + " Stocks of " + s)


            else:
                notification_callback.emit("The single stock is too expensive - skipping")
        else:
            notification_callback.emit("Buying is not allowed in Settings - skipping the buying order")

    def process_candidates(self, notification_callback=None):
        """
processes candidates for buying if enough SMA
        :return:
        """
        requiredCushionForOpenPositions = self.get_required_cushion_for_open_positions()
        remainingFunds = float(self.app.sMa)
        real_remaining_funds = remainingFunds - requiredCushionForOpenPositions
        self.app.smaWithSafety = real_remaining_funds
        if self.settings.USEMARGIN==False:     #if margin not allowed use net liquidation as maximum
            positions_summary=0
            for k,p in self.app.openPositions.values():
                positions_summary+=p["Value"]
            real_remaining_funds=float(self.app.netLiquidation)-float(positions_summary)-float(self.settings.BULCKAMOUNT)
            notification_callback.emit("Using own cash only "+"("+str(real_remaining_funds)+"), margin dismissed in settings")

        if real_remaining_funds < 1000:
            notification_callback.emit("SMA (including open positions cushion) is " + str(
                real_remaining_funds) + " it is less than 1000 - skipping buy")
            return
        else:
            notification_callback.emit(
                "SMA (including open positions cushion) is :" + str(real_remaining_funds) + " searching candidates")
            # updating the targets if market was open in the middle
            self.update_target_price_for_tracked_stocks(notification_callback)
            res = sorted(self.app.candidatesLive.items(), key=lambda x: x[1]['tipranksRank'], reverse=True)
            notification_callback.emit(str(len(res)) + "Candidates found,sorted by Tipranks ranks")
            for i, c in res:
                if self.app.tradesRemaining > 0 or self.app.tradesRemaining == -1:
                    if c['Stock'] in self.app.openPositions:
                        notification_callback.emit("Skipping " + c['Stock'] + " as it is in open positions.")
                        continue
                    elif c['Stock'] in self.app.openOrders.keys():
                        notification_callback.emit("Skipping " + c['Stock'] + " as it is in open orders.")
                        continue
                    else:
                        result=self.evaluate_stock_for_buy(c['Stock'], notification_callback)
                        if result=='bought':
                            break                    #to avoid buying more than one in a worker run
                else:
                    notification_callback.emit("Skipping " + c['Stock'] + " no available trades.")

    def process_positions_candidates(self, status_callback, notification_callback):
        """
Process Open positions and Candidates
        """
        try:
            est = timezone('US/Eastern')
            fmt = '%Y-%m-%d %H:%M:%S'
            local_time = datetime.now().strftime(fmt)
            est_time = datetime.now(est).strftime(fmt)
            notification_callback.emit("-------Starting Worker...----EST Time: " + est_time + "--------------------")

            notification_callback.emit("Checking connection")
            conState = self.app.isConnected()
            if conState:
                notification_callback.emit("Connection is fine- proceeding")
            else:
                notification_callback.emit("Connection lost-reconnecting")
                self.connect_to_tws(notification_callback)

            # collect and update
            self.update_open_orders(notification_callback)
            self.update_open_positions(notification_callback)
            status_callback.emit("Processing Positions-Candidates ")
            if self.trading_session_state == "Open":
                # process
                self.process_candidates(notification_callback)
                self.process_positions(notification_callback)
                self.last_worker_execution_time = datetime.now()
            else:
                # remainingFunds = self.app.sMa
                # existing_positions = self.app.openPositions
                notification_callback.emit("Trading session is not Open - processing skept")

            notification_callback.emit(
                "...............Worker finished....EST Time: " + est_time + "...................")
            status_callback.emit("Connected")
        except Exception as e:
            if hasattr(e, 'message'):
                notification_callback.emit("Error in processing Worker : " + str(e.message))
            else:
                notification_callback.emit("Error in processing Worker : " + str(e))

    def run_loop(self):
        self.app.run()

    def update_open_positions(self, notification_callback=None):
        """
updating all openPositions, refreshed on each worker- to include changes from new positions after BUY
        """
        # update positions from IBKR
        notification_callback.emit("Updating open Positions:")
        print("Request all positions general info")

        self.app.openPositionsLiveDataRequests = {}  # reset requests dictionary as positions could be changed...
        self.app.openPositions = {}  # reset open positions
        self.app.temp_positions = {}

        self.app.finishedPostitionsGeneral = False  # flag to ensure all positions received
        self.app.reqPositions()  # requesting open positions
        time.sleep(0.5)
        counter = 0
        while (self.app.finishedPostitionsGeneral != True):
            print("waiting to get all general positions info: "+str(counter))
            time.sleep(1)
            counter += 1
        for s, p in self.app.temp_positions.items():  # start tracking one by one
            while s not in self.app.openPositions.keys():
                id = self.app.nextorderId
                # self.app.openPositions[s]["tracking_id"] = id
                self.app.openPositionsLiveDataRequests[id] = s
                self.app.reqPnLSingle(id, self.settings.ACCOUNT, "", p["conId"])
                notification_callback.emit("Started tracking " + s + " position PnL")
                self.app.nextorderId += 1
                time.sleep(0.1)

        notification_callback.emit(str(len(self.app.openPositions)) + " open positions completely updated")

    def update_open_orders(self, notification_callback=None):
        """
Requests all open orders
        """
        notification_callback.emit("Updating all open orders")
        self.app.openOrders = {}
        self.app.finishedReceivingOrders = False
        self.app.reqAllOpenOrders()
        # while(self.app.finishedReceivingOrders!=True):
        print("waiting to get all orders info")
        time.sleep(1)

        notification_callback.emit(str(len(self.app.openOrders)) + " open orders found ")

    def start_tracking_excess_liquidity(self, notification_callback=None):
        """
Start tracking excess liquidity - the value is updated every 3 minutes
        """
        # todo: add safety to not buy faster than every 3 minutes
        notification_callback.emit("Starting to track Excess liquidity")
        id = self.app.nextorderId
        self.app.reqAccountSummary(id, "All", "ExcessLiquidity,DayTradesRemaining,NetLiquidation,SMA")
        self.app.nextorderId += 1

    def request_current_PnL(self, notification_callback=None):
        """
Creating a PnL request the result will be stored in generalStarus
        """
        global id, status
        id = self.app.nextorderId
        notification_callback.emit("Requesting Daily PnL")
        self.app.reqPnL(id, self.settings.ACCOUNT, "")
        # time.sleep(0.5)
        self.app.nextorderId = self.app.nextorderId + 1
        notification_callback.emit(self.app.generalStatus)

    def log_decision(self, logFile, order):
        with open(logFile, "a") as f:
            currentDt = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
            order = '\n'+currentDt + '---' + order
            f.write(order)

    def get_required_cushion_for_open_positions(self):
        requiredCushion = 0
        existing_positions = self.app.openPositions
        for k, v in existing_positions.items():
            value = v['Value']
            if value != 0:
                profit = v['UnrealizedPnL']
                clearvalue = value - profit
                canLose = abs(int(self.settings.LOSS))
                requiredcushionForPosition = clearvalue / 100 * canLose
                requiredcushionForPosition += profit
                requiredCushion += requiredcushionForPosition
        return requiredCushion

    def request_ticker_data(self, ticker: str):
        # todo implement ticker data functionality

        contract = createContract(ticker)
        id = self.app.nextorderId
        self.app.contract_processing = True
        self.app.reqContractDetails(self.app.nextorderId, contract)
        self.app.nextorderId = self.app.nextorderId + 1
        while self.app.contract_processing:
            time.sleep(0.1)
        cd = self.app.contractDetailsList[id]
        i = 5
        return cd

    def check_if_holiday(self):
        id = self.app.nextorderId

        first = next(iter(self.settings.CANDIDATES))
        c = createContract(first.ticker)
        self.app.reqContractDetails(id, c)
        while (self.app.trading_hours_received != True):
            print("waiting to get trading session status info")
            time.sleep(1)
        session_info_to_parse = self.app.trading_session
        today_string = session_info_to_parse.split(";")[0]
        if 'CLOSED' in today_string:
            self.trading_session_holiday = True
        else:
            self.trading_session_holiday = False

        self.app.nextorderId += 1

    def add_market_data_to_live_candidates(self, notification_callback):
        for k, v in self.app.candidatesLive.items():
            for dt in self.stocks_data_from_server:
                if dt['ticker'] == v['Stock']:
                    self.app.candidatesLive[k]["averagePriceDropP"] = dt['yahoo_avdropP']
                    self.app.candidatesLive[k]["averagePriceSpreadP"] = dt['yahoo_avspreadP']
                    self.app.candidatesLive[k]['tipranksRank'] = dt['tipranks']
                    notification_callback.emit(
                        "Yahoo data and Tipranks for " + v['Stock'] + " was added")
                    break
