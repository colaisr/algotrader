import json
from datetime import date, datetime

import requests

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def report_login_to_server(settings):
    r = requests.post(settings.SERVERURL + '/connections/logconnection',
                      json={"user": settings.SERVERUSER})
    status_code = r.status_code
    if status_code == 200:
        return r.text

def report_snapshot_to_server(settings, netLiquidation=None, smaWithSafety=None, tradesRemaining=None,
                                      all_positions_values=None, openPositions=None, openOrders=None, dailyPnl=None):
    net_liquidation=netLiquidation
    remaining_sma_with_safety=smaWithSafety
    remaining_trades=tradesRemaining
    all_positions_value=all_positions_values
    open_positions=json.dumps(openPositions,default=lambda o: '<not serializable>')
    open_orders=json.dumps(openOrders,default=lambda o: '<not serializable>')
    dailyPnl=dailyPnl
    r = requests.post(settings.SERVERURL + '/connections/postreport',
                      json={"user": settings.SERVERUSER,
                            "net_liquidation" : net_liquidation,
                            "remaining_sma_with_safety" : remaining_sma_with_safety,
                            "remaining_trades":remaining_trades,
                            "all_positions_value":all_positions_value,
                            "open_positions":open_positions,
                            "open_orders":open_orders,
                            "dailyPnl":dailyPnl})
    status_code = r.status_code
    if status_code == 200:
        return r.text

def report_market_data_to_server(settings,candid_data):
    d=json.dumps(candid_data,default=lambda o: '<not serializable>')
    r = requests.post(settings.SERVERURL + '/marketdata/updatemarketdata',
                      json={"user": settings.SERVERUSER,
                            "tickers":json.dumps(candid_data,default=json_serial)})

    status_code = r.status_code
    if status_code == 200:
        return r.text