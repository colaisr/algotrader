
import yfinance as yf

from DataBase.db import dropCandidateStat, addCandidStat


def updatetMarketStatisticsForCandidates(candidates):
    dropCandidateStat()
    print("Updating the statistics from Yahoo Finance:")
    for f in candidates:

        df=yf.download(f, period = "1y")
        df['drop']=df['Open']-df['Low']
        df['dropP']=df['drop']/df['Open']*100
        df['diffD']=df['Low']-df['High']
        df['diffD']=df['diffD'].abs()
        df['diffP']=df['diffD']/df['Open']*100

        avdropP=df["dropP"].mean()


        avChange=df["diffP"].mean()


        addCandidStat(f,avdropP,avChange)
    print("Statistics updated for ",len(candidates)," candidates")

