import asyncio
import time
import yfinance as yf



TRANDINGSTOCKS = ["AAPL", "FB", "ZG", "MSFT", "NVDA", "TSLA", "BEP", "GOOGL"]
stocksStatistics={}


def get_statistics_to_Stocks(stocks):
    """

    :param stocks: list of stocks to check
    :return: stock-stats dictionary
    """
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(get_all_stocks_statistics(TRANDINGSTOCKS))
        global stocksStatistics
        return stocksStatistics
    except (Exception, KeyboardInterrupt) as e:
        print('ERROR', str(e))


async def get_stock_rank(s):
    print("Getting Statistics  for "+s)
    # notification_callback.emit("Downloading the data for: "+s)

    df=yf.download(s, period = "1y")
    # notification_callback.emit("Figuring average Drop and Change for: "+ s)
    df['drop']=df['Open']-df['Low']
    df['dropP']=df['drop']/df['Open']*100
    df['diffD']=df['Low']-df['High']
    df['diffD']=df['diffD'].abs()
    df['diffP']=df['diffD']/df['Open']*100

    avdropP=df["dropP"].mean()
    avChange=df["diffP"].mean()
    stats={}
    stats['avDrop']=avdropP
    stats['avChange'] = avChange
    print('Got drop of: ' + str(avdropP) + ' for ' + s)
    print('Got change of: ' + str(avChange) + ' for ' + s)

    return s,stats


async def get_all_stocks_statistics(stocks):
    t0 = time.time()
    coroutines = [get_stock_rank(url) for url in stocks]
    results = await asyncio.gather(*coroutines)
    # completed, pending = await asyncio.wait(coroutines)
    for s,r in results:
        global stocksStatistics
        stocksStatistics[s] = r

    t1 = time.time()
    print(f"{t1-t0} seconds to gather {len(stocks)} statistics.")

if __name__ == '__main__':
    try:
        msft = yf.Ticker("MSFrereT")
        f=msft.financials
        print(f)
        u=msft.sustainability
        print(u)
        r=msft.recommendations
        print(r)

        r=2
    except (Exception, KeyboardInterrupt) as e:
        print('ERROR', str(e))
