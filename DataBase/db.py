import datetime
from os import path

from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy import create_engine
DB_PATH='sqlite:///db.db'
engine = create_engine(DB_PATH, echo = True)
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy.orm import sessionmaker

class Position(Base):
   __tablename__ = 'positions'
   id = Column(Integer, primary_key=True)

   stock = Column(String)
   quantity=Column(Float)
   marketValue = Column(Float)
   todayPnL=Column(Float)
   generalpnlP=Column(Float)
   lastUpdate=Column(DateTime)


class Order(Base):
   __tablename__ = 'orders'
   id = Column(Integer, primary_key=True)

   stock = Column(String)
   action=Column(String)
   actionType = Column(String)

class Candidate(Base):
   __tablename__ = 'candidates'
   id = Column(Integer, primary_key=True)

   stock = Column(String)
   bid=Column(Integer)
   ask = Column(Integer)
   lastPrice=Column(Integer)
   close=Column(Integer)
   lastUpdate=Column(DateTime)


class CandidateStat(Base):
   __tablename__ = 'candidatesHistoryStats'
   id = Column(Integer, primary_key=True)

   stock = Column(String)
   averagePriceDrop=Column(Integer)
   averagePriceSpread = Column(Integer)

class CandidateRanks(Base):
   __tablename__ = 'candidatesRanks'
   id = Column(Integer, primary_key=True)

   stock = Column(String)
   tipranksRank=Column(Float)
   yahooRank = Column(Float)


class Deal(Base):
   __tablename__ = 'deals'
   id = Column(Integer, primary_key=True)

   stock = Column(String)
   bought = Column(Integer)
   sold = Column(Integer)
   pnl = Column(Integer)
   pnlInP = Column(Integer)
   openDate=Column(DateTime)
   closeDate=Column(DateTime)


def GetAverageDropForStock(s):
   engine = create_engine(DB_PATH)
   Session = sessionmaker(bind = engine)
   session = Session()
   st=session.query(CandidateStat).filter_by(stock=s).first()
   return st.averagePriceDrop


def GetRanksForStocks():
   engine = create_engine(DB_PATH)
   Session = sessionmaker(bind = engine)
   session = Session()
   result = session.query(CandidateRanks).all()
   resD={}
   for r in result:
      resD[r.stock]={"tipranks":r.tipranksRank,"yahoo":r.yahooRank}
   return resD


def addCandidStat(stock, avPriceDrop, avSpread):

   engine = create_engine(DB_PATH)
   Session = sessionmaker(bind = engine)
   session = Session()
   p = CandidateStat(stock=stock, averagePriceDrop=avPriceDrop, averagePriceSpread=avSpread)
   session.add(p)
   session.commit()


def updateCandidatesInDB(candids):
   engine = create_engine(DB_PATH)
   Session = sessionmaker(bind = engine)
   session = Session()

   for s, v in candids.items():
      p = Candidate(stock=v["Stock"], bid=v["Bid"], ask=v["Ask"],lastPrice=v["LastPrice"],close=v["Close"], lastUpdate=v["LastUpdate"])
      session.add(p)
      session.commit()

def dropPositions():
   engine = create_engine(DB_PATH)
   Session = sessionmaker(bind = engine)
   session = Session()
   session.query(Position).delete()
   session.commit()


def flushOpenPositionsToDB(posFromIbkr):
   engine = create_engine(DB_PATH)
   Session = sessionmaker(bind = engine)
   session = Session()
   dt=datetime.datetime.now()

   for s, v in posFromIbkr.items():
      p = Position(stock=s, quantity=v["stocks"], marketValue=v["Value"],todayPnL=v["DailyPnL"],generalpnlP=v["UnrealizedPnL"], lastUpdate=dt)
      session.add(p)
      session.commit()


def dropCandidateStat():

   engine = create_engine(DB_PATH)
   Session = sessionmaker(bind = engine)
   session = Session()
   session.query(CandidateStat).delete()
   session.commit()


def dropCandidates():
   engine = create_engine(DB_PATH)
   Session = sessionmaker(bind = engine)
   session = Session()
   session.query(Candidate).delete()
   session.commit()


def updateOpenOrdersinDB(ordersFromIBKR):
   engine = create_engine(DB_PATH)
   Session = sessionmaker(bind = engine)
   session = Session()
   dt=datetime.datetime.now()

   for s,v in ordersFromIBKR.items():
      result = session.query(Order).filter(Order.stock == s).all()
      action=v["Action"]
      type=v["Type"]
      if len(result) == 0:
         p = Order(stock=s, action=action, actionType=type)
         session.add(p)
         session.commit()


      else:

         result[0].action=action
         result[0].actionType=type
         session.commit()
         print("Updated in DB : ",s)


def dropOpenOrders():
   engine = create_engine(DB_PATH)
   Session = sessionmaker(bind = engine)
   session = Session()
   session.query(Order).delete()
   session.commit()


def checkDB():
   if path.exists('db.db'):
      pass
   else:
      Base.metadata.create_all(engine)


def updateTipRanksInDB(ranks):
   engine = create_engine(DB_PATH)
   Session = sessionmaker(bind = engine)
   session = Session()

   for s,v in ranks.items():
      result = session.query(CandidateRanks).filter(CandidateRanks.stock == s).all()
      rank=v
      if len(result) == 0:
         p = CandidateRanks(stock=s, tipranksRank=rank, yahooRank=0)
         session.add(p)
         session.commit()


      else:

         result[0].tipranksRank=rank
         session.commit()

   print(len(ranks)," stock ratings updated in the DB from Tiprank")



if __name__ == '__main__':
   Base.metadata.create_all(engine)
