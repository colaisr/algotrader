import configparser
import time
import threading
from  ApiWrapper import IBapi,createContract
from DataBase.db import updateOpenPostionsInDB, updateOpenOrdersinDB, dropPositions, dropOpenOrders
from Research.UpdateCandidates import updatetMarketStatisticsAndCandidates
from ibapi.common import MarketDataTypeEnum




def run_loop():
    app.run()


def get_positions():
    # update positions from IBKR
    print("Updating positions:")
    app.reqPositions()# requesting complete list
    time.sleep(1)
    for s,p in app.openPositions.items():
        id = app.nextorderId
        app.positionDetails[id]={"Stock":s}
        app.reqPnLSingle(id, ACCOUNT, "", p["conId"]);#requesting one by one
        app.nextorderId += 1

    print(len(app.positionDetails)," positions info updated")
    time.sleep(2)
    dropPositions()
    updateOpenPostionsInDB(app.positionDetails)

def get_orders():
    print("Updating all open Orders")
    app.openOrders = {}
    app.reqAllOpenOrders()
    time.sleep(1)
    dropOpenOrders()
    updateOpenOrdersinDB(app.openOrders)

config = configparser.ConfigParser()
config.read('config.ini')
PORT = config['Connection']['portl']
ACCOUNT=config['Account']['accl']
ticksIds={}

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
time.sleep(1)
status=app.generalStatus
print("PnL today status: ")
print(status)

# #take the research from Yahoo
# print("Updating the Statistics: ")
# candidates=updatetMarketStatisticsAndCandidates()
# print("Finished to update the Statistics: ")

get_positions()
get_orders()

print("**********************AllDataPrepared********************")

# #starting querry
# for s in candidates:
#     id=app.nextorderId
#     print("starting to track: ",s,"traking with Id:",id)
#     c=createContract(s)
#     app.reqMarketDataType(1)
#     app.reqMktData(id, c, '', False, False, [])
#     ticksIds[s]=id
#     app.nextorderId += 1






