import datetime
from os import path

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy import create_engine

DB_PATH = 'sqlite:///db.db'
engine = create_engine(DB_PATH, echo=True)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
from sqlalchemy.orm import sessionmaker


class Position(Base):
    __tablename__ = 'positions'
    id = Column(Integer, primary_key=True)

    stock = Column(String)
    quantity = Column(Float)
    marketValue = Column(Float)
    todayPnL = Column(Float)
    generalpnlP = Column(Float)
    lastUpdate = Column(DateTime)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)

    stock = Column(String)
    action = Column(String)
    actionType = Column(String)


class Candidate(Base):
    __tablename__ = 'candidates'
    id = Column(Integer, primary_key=True)

    stock = Column(String)
    bid = Column(Integer)
    ask = Column(Integer)
    lastPrice = Column(Integer)
    open = Column(Integer)
    close = Column(Integer)
    tipranksRank = Column(Float)
    averagePriceDropP = Column(Integer)
    averagePriceSpreadP = Column(Integer)
    lastUpdate = Column(DateTime)


class Deal(Base):
    __tablename__ = 'deals'
    id = Column(Integer, primary_key=True)

    stock = Column(String)
    cand_bid = Column(Float)
    cand_ask = Column(Float)
    cand_lastPrice = Column(Float)
    cand_open = Column(Float)
    cand_close = Column(Float)
    cand_high = Column(Float)
    cand_low = Column(Float)
    cand_avPriceDrop_Percent = Column(Float)
    cand_avPriceSpread_Percent = Column(Float)
    cand_targetPrice = Column(Float)
    cand_tipRank = Column(Integer)
    cand_updated = Column(DateTime)

    order_price = Column(Float)
    order_quantity = Column(Integer)
    order_placed = Column(DateTime)

    deal_lastStatus = Column(String)
    deal_statusUpdated = Column(DateTime)

    deal_isClosed = Column(Boolean)


def add_deal_for_candidate(candidate, price, orderVolume, addTime):
    engine = create_engine(DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()
    d = Deal(stock=candidate["Stock"],
             cand_bid=candidate["Bid"],
             cand_ask=candidate["Ask"],
             cand_lastPrice=candidate["LastPrice"],
             cand_open=candidate["Open"],
             cand_close=candidate["Close"],
             cand_high=candidate["High"],
             cand_low=candidate["Low"],
             cand_avPriceDrop_Percent=candidate["averagePriceDropP"],
             cand_avPriceSpread_Percent=candidate["averagePriceSpreadP"],
             cand_targetPrice=candidate["target_price"],
             cand_tipRank=candidate["tipranksRank"],
             cand_updated=candidate["LastUpdate"],
             order_price=price,
             order_quantity=orderVolume,
             order_placed=addTime,
             deal_lastStatus="never updated",
             deal_statusUpdated=addTime,
             deal_isClosed=False)

    session.add(d)
    session.commit()


def dropLiveCandidates():
    engine = create_engine(DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(Candidate).delete()
    session.commit()


def flushLiveCandidatestoDB(candids):
    engine = create_engine(DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()

    for s, v in candids.items():
        p = Candidate(stock=v["Stock"],
                      bid=v["Bid"],
                      ask=v["Ask"],
                      lastPrice=v["LastPrice"],
                      open=v["Open"],
                      close=v["Close"],
                      averagePriceDropP=v["averagePriceDropP"],
                      averagePriceSpreadP=v["averagePriceSpreadP"],
                      tipranksRank=v["tipranksRank"],
                      lastUpdate=v["LastUpdate"])
        session.add(p)
        session.commit()


def dropPositions():
    engine = create_engine(DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(Position).delete()
    session.commit()


def flushOpenPositionsToDB(posFromIbkr):
    engine = create_engine(DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()
    dt = datetime.datetime.now()

    for s, v in posFromIbkr.items():
        p = Position(stock=s, quantity=v["stocks"], marketValue=v["Value"], todayPnL=v["DailyPnL"],
                     generalpnlP=v["UnrealizedPnL"], lastUpdate=dt)
        session.add(p)
        session.commit()


def dropOpenOrders():
    engine = create_engine(DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(Order).delete()
    session.commit()


def updateOpenOrdersinDB(ordersFromIBKR):
    engine = create_engine(DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()
    dt = datetime.datetime.now()

    for s, v in ordersFromIBKR.items():
        result = session.query(Order).filter(Order.stock == s).all()
        action = v["Action"]
        type = v["Type"]
        if len(result) == 0:
            p = Order(stock=s, action=action, actionType=type)
            session.add(p)
            session.commit()


        else:

            result[0].action = action
            result[0].actionType = type
            session.commit()
            print("Updated in DB : ", s)


def updatetMarketStatisticsForCandidateFromDB(s):
    engine = create_engine(DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()
    c = session.query(Candidate).filter(Candidate.stock == s).all()

    if len(c) > 0:
        return c[0].averagePriceDropP, c[0].averagePriceSpreadP
    else:
        return 0, 0


def getRatingsForAllCandidatesFromDB():
    engine = create_engine(DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()
    c = session.query(Candidate).all()
    stocksRanks = {}
    if len(c) > 0:
        for s in c:
            stocksRanks[s.stock] = s.tipranksRank
    return stocksRanks


def checkDB():
    if path.exists('db.db'):
        pass
    else:
        Base.metadata.create_all(engine)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
