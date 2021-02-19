import json
from datetime import date, datetime


import requests


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def report_market_action(settings, symbol, shares, price, side, time):
    time_to_report = datetime.strptime(time, '%Y%m%d %H:%M:%S')
    r = requests.post(settings.SERVERURL + '/connections/postexecution',
                      json={"user": settings.SERVERUSER,
                            "symbol": symbol,
                            "shares": shares,
                            "price": price,
                            "side": side,
                            "time": json.dumps(time_to_report, default=json_serial)})
    status_code = r.status_code
    if status_code == 200:
        print("Successfully reported execution to server")
    else:
        print("Execution transmit failed")


def get_market_data_from_server(settings, candidates):
    c = json.dumps(candidates)
    r = requests.get(settings.SERVERURL + '/marketdata/retrievemarketdata',
                     json={"user": settings.SERVERUSER,
                           "tickers": c})

    status_code = r.status_code
    if status_code == 200:
        t=r.text
        decoded_list=json.loads(t)
        result=[]
        [result.append(json.loads(v)) for v in decoded_list.values()]
        for it in result:
            it['updated']=datetime.fromisoformat(it['updated'])
        return result


def report_login_to_server(settings):
    r = requests.post(settings.SERVERURL + '/connections/logconnection',
                      json={"user": settings.SERVERUSER})
    status_code = r.status_code
    if status_code == 200:
        return r.text


def report_snapshot_to_serverO(status_callback, notification_callback,settings, netLiquidation=None, smaWithSafety=None, tradesRemaining=None,
                              all_positions_values=None, openPositions=None, openOrders=None, dailyPnl=None):
    net_liquidation = netLiquidation
    remaining_sma_with_safety = smaWithSafety
    remaining_trades = tradesRemaining
    all_positions_value = all_positions_values
    open_positions = json.dumps(openPositions, default=lambda o: '<not serializable>')
    open_orders = json.dumps(openOrders, default=lambda o: '<not serializable>')
    dailyPnl = dailyPnl
    r = requests.post(settings.SERVERURL + '/connections/postreport',
                      json={"user": settings.SERVERUSER,
                            "net_liquidation": net_liquidation,
                            "remaining_sma_with_safety": remaining_sma_with_safety,
                            "remaining_trades": remaining_trades,
                            "all_positions_value": all_positions_value,
                            "open_positions": open_positions,
                            "open_orders": open_orders,
                            "dailyPnl": dailyPnl})
    status_code = r.status_code
    if status_code == 200:
        return r.text


def report_snapshot_to_server(*args, **kwargs):
    arguments=args[1]
    net_liquidation = arguments[1]
    remaining_sma_with_safety = arguments[2]
    remaining_trades = arguments[3]
    all_positions_value = arguments[4]
    open_positions = json.dumps(arguments[5], default=lambda o: '<not serializable>')
    open_orders = json.dumps(arguments[6], default=lambda o: '<not serializable>')
    dailyPnl = arguments[7]
    r = requests.post(arguments[0].SERVERURL + '/connections/postreport',
                      json={"user": arguments[0].SERVERUSER,
                            "net_liquidation": net_liquidation,
                            "remaining_sma_with_safety": remaining_sma_with_safety,
                            "remaining_trades": remaining_trades,
                            "all_positions_value": all_positions_value,
                            "open_positions": open_positions,
                            "open_orders": open_orders,
                            "dailyPnl": dailyPnl})
    status_code = r.status_code
    if status_code == 200:
        return r.text
    return "great succedd"

def report_market_data_to_server(settings, candid_data):
    d = json.dumps(candid_data, default=lambda o: '<not serializable>')
    r = requests.post(settings.SERVERURL + '/marketdata/updatemarketdata',
                      json={"user": settings.SERVERUSER,
                            "tickers": json.dumps(candid_data, default=json_serial)})

    status_code = r.status_code
    if status_code == 200:
        return r.text
