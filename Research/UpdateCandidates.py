
import yfinance as yf



def updatetMarketStatisticsForCandidate(s):
    print("Updating the statistics from Yahoo Finance for: ",s)

    df=yf.download(s, period = "1y")
    df['drop']=df['Open']-df['Low']
    df['dropP']=df['drop']/df['Open']*100
    df['diffD']=df['Low']-df['High']
    df['diffD']=df['diffD'].abs()
    df['diffP']=df['diffD']/df['Open']*100

    avdropP=df["dropP"].mean()
    avChange=df["diffP"].mean()

    return avdropP,avChange
