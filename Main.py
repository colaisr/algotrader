import configparser
import sched
import time
import threading
from datetime import datetime

from ApiWrapper import IBapi, createContract, createTrailingStopOrder
from DataBase.db import updateOpenPostionsInDB, updateOpenOrdersinDB, dropPositions, dropOpenOrders, dropCandidates, \
    updateCandidatesInDB
from pytz import timezone

config = configparser.ConfigParser()
config.read('config.ini')
PORT = config['Connection']['portp']
ACCOUNT=config['Account']['accp']
INTERVAL = config['Connection']['interval']
#algo
PROFIT=config['Algo']['gainP']
TRAIL=config['Algo']['trailstepP']
TRANDINGSTOCKS=["AAPL","FB","ESPO","ZG","MSFT","NVDA","TSLA","BEP","GOOG"]

def init_candidates():
    #starting querry
    for s in TRANDINGSTOCKS:
        id=app.nextorderId
        print("starting to track: ",s,"traking with Id:",id)
        c=createContract(s)
        app.candidates[id] = {"Stock": s,
                              "Close": "-",
                              "Bid": "-",
                              "Ask": "-",
                              "LastPrice": "-",
                              "LastUpdate": "-"}
        app.reqMarketDataType(1)
        app.reqMktData(id, c, '', False, False, [])
        app.nextorderId += 1
        time.sleep(0.5)



def processProfits():
    print("Processing profits")
    for i,p in app.positionDetails.items():
        if p["Value"]==0:
            continue
        profit=p["UnrealizedPnL"]/p["Value"]*100
        if profit>float(PROFIT):
            orders=app.openOrders
            if p["Stock"] in orders:
                print("Order for ",p["Stock"],"already exist- skipping")
            else:
                print("Profit for: ", p["Stock"], " is ", profit,"Creating a trailing Stop Order")
                contract=createContract(p["Stock"])
                order=createTrailingStopOrder(p["Position"],TRAIL)
                app.placeOrder(app.nextorderId, contract, order)
                app.nextorderId = app.nextorderId + 1
                print("Created a Trailing Stop order for ",p["Stock"]," at level of ",TRAIL,"%")


s = sched.scheduler(time.time, time.sleep)
def workerGo(sc):
    est = timezone('EST')
    fmt = '%Y-%m-%d %H:%M:%S'
    time=datetime.now(est).strftime(fmt)

    print("---------------Processing Worker...-------EST Time: ",time,"--------------------")
    #collect and update
    updateOrders()
    updatePositions()
    updateCandidates()

    #process
    processProfits()
    print("...............Worker finished.........................")

    s.enter(float(INTERVAL), 1, workerGo, (sc,))


def run_loop():
    app.run()


def updatePositions():
    dropPositions()
    updateOpenPostionsInDB(app.positionDetails)
    print(len(app.positionDetails), " positions info updated")

def updateCandidates(): #todo background for db
    dropCandidates()
    updateCandidatesInDB(app.candidates)
    print(len(app.candidates), " candidates info updated")


def get_positions():
    # update positions from IBKR
    print("Updating positions:")
    app.reqPositions()# requesting complete list
    time.sleep(1)
    for s,p in app.openPositions.items():#start tracking one by one
        id = app.nextorderId
        app.positionDetails[id]={"Stock":s}
        app.reqPnLSingle(id, ACCOUNT, "", p["conId"]);#requesting one by one
        app.nextorderId += 1
        
    time.sleep(2)
    updatePositions()


def updateOrders():
    print("Updating all open Orders")
    app.openOrders = {}
    app.reqAllOpenOrders()
    time.sleep(1)
    dropOpenOrders()
    updateOpenOrdersinDB(app.openOrders)
    print(len(app.openOrders), " Orders found and saved to DB")


print("Starting Todays session:",time.ctime())

app = IBapi()
app.connect('127.0.0.1', int(PORT), 123)
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

id=app.nextorderId

#General Account info:
app.reqPnL(id,ACCOUNT,"")
app.nextorderId=app.nextorderId+1
time.sleep(2)
status=app.generalStatus
print("PnL today status: ")
print(status)

#todo add the statistics to the candidates
# #take the research from Yahoo
# print("Updating the Statistics: ")
# candidates=updatetMarketStatisticsAndCandidates()
# print("Finished to update the Statistics: ")

#start tracking open positions
get_positions()

#start tracking candidates
init_candidates()
print("**********************Connected starting Worker********************")
#starting worker in loop...
s.enter(2, 1, workerGo, (s,))
s.run()









