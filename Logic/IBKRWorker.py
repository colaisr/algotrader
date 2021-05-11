import time
import threading
import datetime

from Logic.ApiWrapper import IBapi, createContract, createTrailingStopOrder, create_limit_buy_order, createMktSellOrder
from pytz import timezone

from twsapi.ibapi.execution import ExecutionFilter


class IBKRWorker():
    def __init__(self, settings):
        self.trading_session_state=None
        self.app = IBapi()
        self.settings = settings
        self.app.setting = self.settings
        self.stocks_data_from_server = []
        self.last_worker_execution_time=None

    def run_full_cycle(self):
        try:
            connected=self.connect_to_tws()
            if connected:
                self.check_if_holiday()
                self.prepare_and_track()
                self.process_positions_candidates()
                return True
            else:
                print("Could not connect to TWS ....processing skept..")
                return False
        except Exception as e:
            self.app.disconnect()
            self.app.reset()
            if hasattr(e, 'message'):
                print("Error in IBKR processing : " + str(e.message))
            else:
                print("Error in IBKR processing : " + str(e))

    def prepare_and_track(self):
        """
Connecting to IBKR API and initiating the connection instance
        :return:
        """
        print("Connecting")
        try:
            print("Begin prepare and connect")
            self.request_current_PnL()
            self.start_tracking_excess_liquidity()
            self.check_todays_executions()
            self.update_open_positions()

            # request open orders
            self.update_open_orders()
            # start tracking candidates
            succeed=self.evaluate_and_track_candidates()
            if not succeed:
                raise Exception('Problem retrieving market data from TWS more than 60 sec')
            self.update_target_price_for_tracked_stocks()
            print("Connected to IBKR and READY")
            print("Connected and ready")

        except Exception as e:
            if hasattr(e, 'message'):
                print("Error in connection and preparation : " + str(e.message))
            else:
                print("Error in connection and preparation : " + str(e))

    def connect_to_tws(self):
        """
Creates the connection - starts listner for events
        """

        self.app.nextorderId = None
        # while not isinstance(self.app.nextorderId, int):
        retries = 0
        print("Restarting connection to IBKR")
        self.app.disconnect()
        #self.app.reset()
        self.app.connect('127.0.0.1', int(self.settings.PORT), 123)

        # Start the socket in a thread
        api_thread = threading.Thread(target=self.run_loop, name='ibkrConnection', daemon=True)
        api_thread.start()

        # Check if the API is connected via orderid

        while True:
            if isinstance(self.app.nextorderId, int):
                print('Successfully connected to API')
                connected=True
                break
            else:
                print('Waiting for connection...attempt:' + str(retries))
                time.sleep(1)
                retries = retries + 1
                if retries > 10:
                    connected = False
                    break
        if not connected:
            self.app.disconnect()
            self.app.reset()
        return connected

    def evaluate_and_track_candidates(self):
        """
Starts tracking the Candidates and adds the statistics
        """
        time.sleep(1) # clearing messages
        stock_names = [o['ticker'] for o in self.stocks_data_from_server]
        print("Starting to track " + ','.join(stock_names) + " Candidates")

        stock_names=stock_names[0:80]   #trimming 90 queries to track less than 100
        # starting querry
        trackedStockN = 1
        message_number=0
        for s in stock_names:
            id = self.app.nextorderId
            print(
                "starting to track: " + str(trackedStockN) + " of " + str(
                    len(stock_names)) + " " + s +
                " traking with Id:" +
                str(id))
            c = createContract(s)
            self.app.candidatesLive[id] = {"Stock": s,
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
            message_number+=1
            if message_number % 10==0:
                time.sleep(2)
                print("Waiting to clear messages buffer")


        have_empty = True
        counter = 0
        while have_empty:
            time.sleep(1)
            print("Waiting for last requested candidate Close price :" + str(counter))
            closings = [str(x['Close']) for x in self.app.candidatesLive.values()]
            if '-' in closings:
                have_empty = True
            else:
                have_empty = False
            counter += 1
            if counter>60:
                return False



        self.add_market_data_to_live_candidates()

        print(str(len(self.app.candidatesLive)) + " Candidates evaluated and started to track")
        return True

    def process_positions(self):
        """
Processes the positions to identify Profit/Loss
        """
        print("Processing profits")

        for s, p in self.app.openPositions.items():
            if 'Value' in p.keys():
                if p["Value"] != 0:
                    print("Processing " + s)
                    profit = p["UnrealizedPnL"] / p["Value"] * 100
                    print("The profit for " + s + " is " + str(profit) + " %")
                    if profit > float(self.settings.PROFIT):
                        orders = self.app.openOrders
                        if s in orders:
                            print("Order for " + s + "already exist- skipping")
                        elif int(p["stocks"]) < 0:
                            print(
                                "The " + s + " is SHORT position number of stocks is negative: " + p["stocks"])
                        else:
                            print("Profit for: " + s + " is " + str(profit) +
                                                       "Creating a trailing Stop Order to take a Profit")
                            contract = createContract(s)
                            order = createTrailingStopOrder(p["stocks"], self.settings.TRAIL)

                            self.app.placeOrder(self.app.nextorderId, contract, order)
                            self.app.nextorderId = self.app.nextorderId + 1
                            print("Created a Trailing Stop order for " + s + " at level of " +
                                                       str(self.settings.TRAIL) + "%")
                    elif profit < float(self.settings.LOSS):
                        orders = self.app.openOrders
                        if s in orders:
                            print("Order for " + s + "already exist- skipping")
                        else:
                            print("loss for: " + s + " is " + str(profit) +
                                                       "Creating a Market Sell Order to minimize the Loss")
                            contract = createContract(s)
                            order = createMktSellOrder(p['stocks'])
                            self.app.placeOrder(self.app.nextorderId, contract, order)
                            self.app.nextorderId = self.app.nextorderId + 1
                            print("Created a Market Sell order for " + s)

                else:
                    print("Position " + s + " skept its Value is 0")
            else:
                print("Position " + s + " skept it has no Value")

    def evaluate_stock_for_buy(self, s):
        """
Evaluates stock for buying
        :param s:
        """
        ask_price=None
        target_price=None
        tipRank=None
        average_daily_dropP=None
        print("Evaluating " + s + "for a Buy")
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
            print('The market is closed skipping...')
            result='skept'
        elif ask_price < target_price and float(tipRank) > 8:
            self.buy_the_stock(ask_price, s)
            result='bought'

        else:
            print(
                "The price of :" + str(ask_price) + "was not in range of :" + str(average_daily_dropP) + " % " +
                " Or the Rating of " + str(tipRank) + " was not good enough")
            result='skept'

        return result

    def update_target_price_for_tracked_stocks(self):
        """
Update target price for all tracked stocks
        :return:
        """
        print("Updating target prices for Candidates")
        for c in self.app.candidatesLive.values():
            print("Updating target price for " + c["Stock"])
            close = c["Close"]
            open = c["Open"]
            average_daily_dropP = c["averagePriceDropP"]

            if open != '-':  # market is closed
                c["target_price"] = open - open / 100 * average_daily_dropP
                print("Target price for " + str(c["Stock"]) + " updated to " + str(
                    c["target_price"]) + " based on Open price")
            elif close != '-':  # market is open
                c["target_price"] = close - close / 100 * average_daily_dropP
                print("Target price for " + str(c["Stock"]) + " updated to " + str(
                    c["target_price"]) + " based on Close price")
            else:

                c["target_price"] = 0
                print("Skept target price for " + str(c["Stock"]) + "Closing price missing")
                continue

    def buy_the_stock(self, price, s):
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
                print(
                    "Issued the BUY order at " + str(price) + "for " + str(stocksToBuy) + " Stocks of " + s)

            else:
                print("The single stock is too expensive - skipping")
        else:
            print("Buying is not allowed in Settings - skipping the buying order")

    def process_candidates(self):
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
            for k,p in self.app.openPositions.items():
                positions_summary+=p["Value"]
            real_remaining_funds=float(self.app.netLiquidation)-float(positions_summary)
            print("Using own cash only "+"("+str(real_remaining_funds)+"), margin dismissed in settings")

        if real_remaining_funds < 1000:
            print("SMA (including open positions cushion) is " + str(
                real_remaining_funds) + " it is less than 1000 - skipping buy")
            return
        else:
            print(
                "SMA (including open positions cushion) is :" + str(real_remaining_funds) + " searching candidates")
            # updating the targets if market was open in the middle
            self.update_target_price_for_tracked_stocks()
            res = sorted(self.app.candidatesLive.items(), key=lambda x: x[1]['tipranksRank'], reverse=True)
            print(str(len(res)) + "Candidates found,sorted by Tipranks ranks")
            for i, c in res:
                if self.app.tradesRemaining > 0 or self.app.tradesRemaining == -1:
                    if c['Stock'] in self.app.openPositions:
                        print("Skipping " + c['Stock'] + " as it is in open positions.")
                        continue
                    elif c['Stock'] in self.app.openOrders.keys():
                        print("Skipping " + c['Stock'] + " as it is in open orders.")
                        continue
                    else:
                        result=self.evaluate_stock_for_buy(c['Stock'])
                        if result=='bought':
                            break                    #to avoid buying more than one in a worker run
                else:
                    print("Skipping " + c['Stock'] + " no available trades.")

    def process_positions_candidates(self):
        """
Process Open positions and Candidates
        """
        try:
            est = timezone('US/Eastern')
            fmt = '%Y-%m-%d %H:%M:%S'
            est_time = datetime.datetime.now(est).strftime(fmt)
            print("-------Starting Worker...----EST Time: " + est_time + "--------------------")
            print("Processing Positions-Candidates ")
            if self.trading_session_state == "Open":
                # process
                self.process_candidates()
                self.process_positions()
                self.last_worker_execution_time = datetime.datetime.now()
            else:
                print("Trading session is not Open - processing skept")

            print(
                "...............Worker finished....EST Time: " + est_time + "...................")
            self.app.disconnect()
            #self.app.reset()
        except Exception as e:
            if hasattr(e, 'message'):
                print("Error in processing Worker : " + str(e.message))
            else:
                print("Error in processing Worker : " + str(e))

    def run_loop(self):
        self.app.run()

    def update_open_positions(self):
        """
updating all openPositions, refreshed on each worker- to include changes from new positions after BUY
        """
        # update positions from IBKR
        print("Updating open Positions:")
        self.app.openPositionsLiveDataRequests = {}  # reset requests dictionary as positions could be changed...
        self.app.openPositions = {}  # reset open positions
        self.app.temp_positions = {}

        self.app.finishedPostitionsGeneral = False  # flag to ensure all positions received
        self.app.reqPositions()  # requesting open positions
        time.sleep(0.5)
        counter = 0
        while (self.app.finishedPostitionsGeneral != True):
            time.sleep(1)
            counter += 1
        for s, p in self.app.temp_positions.items():  # start tracking one by one
            while s not in self.app.openPositions.keys():
                id = self.app.nextorderId
                # self.app.openPositions[s]["tracking_id"] = id
                self.app.openPositionsLiveDataRequests[id] = s
                self.app.reqPnLSingle(id, self.settings.ACCOUNT, "", p["conId"])
                print("Started tracking " + s + " position PnL")
                self.app.nextorderId += 1
                time.sleep(0.1)

        print(str(len(self.app.openPositions)) + " open positions completely updated")

    def update_open_orders(self):
        """
Requests all open orders
        """
        print("Updating all open orders")
        self.app.openOrders = {}
        self.app.finishedReceivingOrders = False
        self.app.reqAllOpenOrders()
        # while(self.app.finishedReceivingOrders!=True):
        time.sleep(1)

        print(str(len(self.app.openOrders)) + " open orders found ")

    def start_tracking_excess_liquidity(self):
        """
Start tracking excess liquidity - the value is updated every 3 minutes
        """
        # todo: add safety to not buy faster than every 3 minutes
        print("Starting to track Excess liquidity")
        id = self.app.nextorderId
        self.app.reqAccountSummary(id, "All", "ExcessLiquidity,DayTradesRemaining,NetLiquidation,SMA")
        self.app.nextorderId += 1

    def request_current_PnL(self):
        """
Creating a PnL request the result will be stored in generalStarus
        """
        global id, status
        id = self.app.nextorderId
        print("Requesting Daily PnL")
        self.app.reqPnL(id, self.settings.ACCOUNT, "")
        # time.sleep(0.5)
        self.app.nextorderId = self.app.nextorderId + 1
        print(self.app.generalStatus)

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
        c = createContract('AAPL')# checked always with AAPL - can be no candidates
        self.app.reqContractDetails(id, c)
        while (self.app.trading_hours_received != True):
            time.sleep(1)
        session_info_to_parse = self.app.trading_session
        today_string = session_info_to_parse.split(";")[0]
        if 'CLOSED' in today_string:
            self.trading_session_holiday = True
        else:
            self.trading_session_holiday = False
            self.check_session_state()

        self.app.nextorderId += 1

    def add_market_data_to_live_candidates(self):
        for k, v in self.app.candidatesLive.items():
            for dt in self.stocks_data_from_server:
                if dt['ticker'] == v['Stock']:
                    self.app.candidatesLive[k]["averagePriceDropP"] = dt['yahoo_avdropP']
                    self.app.candidatesLive[k]["averagePriceSpreadP"] = dt['yahoo_avspreadP']
                    self.app.candidatesLive[k]['tipranksRank'] = dt['tipranks']
                    self.app.candidatesLive[k]['fmp_rating'] = dt['fmp_rating']
                    print(
                        "Yahoo data and Tipranks for " + v['Stock'] + " was added")
                    break

    def check_session_state(self):
        tz = timezone('US/Eastern')
        current_est_time=datetime.datetime.now(tz).time()
        dstart = datetime.time(4, 0, 0)
        dend=datetime.time(20, 0, 0)
        tstart=datetime.time(9, 30, 0)
        tend=datetime.time(16, 0, 0)
        if time_in_range(dstart,tstart,current_est_time):
            self.trading_session_state = "Pre Market"
        elif time_in_range(tstart,tend,current_est_time):
            self.trading_session_state = "Open"
        elif time_in_range(tend,dend,current_est_time):
            self.trading_session_state = "After Market"
        else:
            self.trading_session_state = "Closed"
        self.app.trading_session_state = self.trading_session_state

    def check_todays_executions(self):
        self.app.executions_received=False
        id = self.app.nextorderId
        self.app.reqExecutions(id, ExecutionFilter())
        while (self.app.executions_received != True):
            time.sleep(1)

        self.app.nextorderId += 1


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end
