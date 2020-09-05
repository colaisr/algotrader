
import yfinance as yf

candidates=["AAPL","FB","ESPO","ZG","MSFT","NVDA","TSLA","BEP","GOOG"]

def updatetMarketStatisticsAndCandidates():

    for f in candidates:

        df=yf.download(f, period = "1y")
        df['drop']=df['Open']-df['Low']
        df['dropP']=df['drop']/df['Open']*100
        df['diffD']=df['Low']-df['High']
        df['diffD']=df['diffD'].abs()
        df['diffP']=df['diffD']/df['Open']*100

        avdropP=df["dropP"].mean()


        avChange=df["diffP"].mean()

        lastP=df.tail(1).iloc[0]['Open']

        priceToBuy=lastP - lastP/100*avdropP
        i, d = divmod(1000/lastP, 1)
        stocksInBulk =i


        # updateCandidate(f,avdropP,avChange,stocksInBulk,lastP,priceToBuy)

    return candidates


if __name__ == '__main__':
    updatetMarketStatisticsAndCandidates()