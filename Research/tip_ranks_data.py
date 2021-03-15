import requests

def get_tr_rating_for_ticker(param):
    url = "https://www.tipranks.com/api/stocks/stockAnalysisOverview/?tickers=" + param

    url = requests.get(url)
    result=url.json()
    score=result[0]['smartScore']
    return score