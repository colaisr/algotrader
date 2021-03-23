def get_rating_for_ticker(param):
    import requests
    url = "https://www.tipranks.com/api/stocks/stockAnalysisOverview/?tickers=" + param

    url = requests.get(url)
    result=url.json()
    score=result[0]['smartScore']



if __name__ == '__main__':

    TRANDINGSTOCKS = ["AAPL", "FB", "ZG", "MSFT", "NVDA", "TSLA", "BEP", "GOOGL"]
    rating=get_rating_for_ticker(TRANDINGSTOCKS[0])