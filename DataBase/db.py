import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy import create_engine
engine = create_engine('sqlite:///db.db', echo = True)
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
   bulksize=Column(Integer)
   averagePriceDrop=Column(Integer)
   averagePriceSpread = Column(Integer)
   dayStartPrice=Column(Integer)
   buyAtPrice=Column(Integer)


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



# Base.metadata.create_all(engine)


def updateCandidate(stock,avDrop,avSpread,bulk,todayOpen,priceToBuy):
   engine = create_engine('sqlite:////Users/colakamornik/Desktop/algotrader/DataBase/db.db')
   Session = sessionmaker(bind = engine)
   session = Session()

   result = session.query(Candidate).filter(Candidate.stock==stock).all()
   if len(result)==0:
      c1 = Candidate(stock=stock,
                     averagePriceDrop=avDrop,
                     averagePriceSpread=avSpread,
                     bulksize=bulk,
                     dayStartPrice=todayOpen,
                     buyAtPrice=priceToBuy)
      session.add(c1)
      session.commit()
   else:
      result[0].averagePriceDrop=avDrop
      result[0].averagePriceSpread = avSpread
      result[0].bulksize=bulk
      result[0].dayStartPrice=todayOpen
      result[0].buyAtPrice=priceToBuy
      session.commit()



   print("Data for :"+stock+" added successfully")


def updateOpenPostionsInDB(posFromIbkr):
   # print("updating the DB Positions")
   engine = create_engine('sqlite:////Users/colakamornik/Desktop/algotrader/DataBase/db.db')
   Session = sessionmaker(bind = engine)
   session = Session()
   dt=datetime.datetime.now()

   for s, v in posFromIbkr.items():
      p = Position(stock=v["Stock"], quantity=v["Position"], marketValue=v["Value"],todayPnL=v["DailyPnL"],generalpnlP=v["UnrealizedPnL"], lastUpdate=dt)
      session.add(p)
      session.commit()
      # print("Added to DB : ", v["Stock"])

   # print("Finished updating DB Positions")
   # for s,v in posFromIbkr.items():
   #    result = session.query(Position).filter(Position.stock == s).all()
   #    stocks=v["stocks"]
   #    cost=v["cost"]
   #    if len(result) == 0:
   #       p = Position(stock=s, quantity=stocks, currentValue=stocks*cost, lastUpdate=dt)
   #       session.add(p)
   #       session.commit()
   #       print("Added to DB : ", s)
   #
   #    else:
   #
   #       result[0].quantity=stocks
   #       result[0].currentValue=stocks*cost
   #       result[0].lastUpdate=dt
   #       session.commit()
   #       print("Updated in DB : ",s)


def dropPositions():
   # print("Clearing the DB Positions")
   engine = create_engine('sqlite:////Users/colakamornik/Desktop/algotrader/DataBase/db.db')
   Session = sessionmaker(bind = engine)
   session = Session()
   session.query(Position).delete()
   session.commit()
   # print("All OpenPositions dropped")

def updateOpenOrdersinDB(ordersFromIBKR):
   # print("updating the DB Orders")
   engine = create_engine('sqlite:////Users/colakamornik/Desktop/algotrader/DataBase/db.db')
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
         # print("Added to DB : ", s," ",action," ",type)

      else:

         result[0].action=action
         result[0].actionType=type
         session.commit()
         print("Updated in DB : ",s)

   # print("Finished updating DB Orders")

def dropOpenOrders():
   # print("Clearing the DB OpenOrders")
   engine = create_engine('sqlite:////Users/colakamornik/Desktop/algotrader/DataBase/db.db')
   Session = sessionmaker(bind = engine)
   session = Session()
   session.query(Order).delete()
   session.commit()
   # print("All OpenOrders dropped")


