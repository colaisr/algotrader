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
        t = r.text
        decoded_list = json.loads(t)
        result = []
        [result.append(json.loads(v)) for v in decoded_list.values()]
        for it in result:
            it['updated'] = datetime.fromisoformat(it['updated'])
        return result


def get_user_settings_from_server(server,user):
    r = requests.get(server + '/algotradersettings/retrieveusersettings',
                     json={"user": user})

    status_code = r.status_code
    if status_code == 200:
        t = r.text
        temp = json.loads(t)
        settings_dictionary = json.loads(temp)

        return settings_dictionary


def report_login_to_server(settings):
    r = requests.post(settings.SERVERURL + '/connections/logconnection',
                      json={"user": settings.SERVERUSER})
    status_code = r.status_code
    if status_code == 200:
        return r.text


def report_snapshot_to_server(*args, **kwargs):
    report_time = datetime.now().isoformat()
    arguments = args[1]
    net_liquidation = arguments[1]
    remaining_sma_with_safety = arguments[2]
    remaining_trades = arguments[3]
    all_positions_value = arguments[4]
    open_positions = json.dumps(arguments[5], default=lambda o: '<not serializable>')
    open_orders = json.dumps(arguments[6], default=lambda o: '<not serializable>')
    dailyPnl = arguments[7]
    last_worker_run = arguments[8]
    if last_worker_run is None:
        last_worker_run = date(1900, 1, 1)
    market_time = arguments[9]
    market_state = arguments[10]
    r = requests.post(arguments[0].SERVERURL + '/connections/postreport',
                      json={"user": arguments[0].SERVERUSER,
                            "net_liquidation": net_liquidation,
                            "report_time": report_time,
                            "remaining_sma_with_safety": remaining_sma_with_safety,
                            "remaining_trades": remaining_trades,
                            "all_positions_value": all_positions_value,
                            "open_positions": open_positions,
                            "open_orders": open_orders,
                            "last_worker_run": last_worker_run.isoformat(),
                            "dailyPnl": dailyPnl,
                            "market_time": market_time.isoformat(),
                            "market_state": market_state})
    status_code = r.status_code
    if status_code == 200:
        return r.text
    return "bad response from server"


def report_market_data_to_server(settings, candid_data):
    d = json.dumps(candid_data, default=lambda o: '<not serializable>')
    r = requests.post(settings.SERVERURL + '/marketdata/updatemarketdata',
                      json={"user": settings.SERVERUSER,
                            "tickers": json.dumps(candid_data, default=json_serial)})

    status_code = r.status_code
    if status_code == 200:
        return r.text

def get_user_candidates_from_server(url,user,use_system_candidates):

    r = requests.get(url + '/userview/retrieveusercandidates',
                     json={"user": user,
                           "use_system_candidates": use_system_candidates})

    status_code = r.status_code
    if status_code == 200:
        t = r.text
        decoded_list = json.loads(t)
        # result = []
        # [result.append(json.loads(v)) for v in decoded_list.values()]
        # for it in result:
        #     it['updated'] = datetime.fromisoformat(it['updated'])
        return decoded_list