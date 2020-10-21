import datetime
from os import path

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

DB_PATH = 'sqlite:///db.db'

Base = declarative_base()


class Deal(Base):
    __tablename__ = 'deals'
    id = Column(Integer, primary_key=True)

    stock = Column(String)
    cand_bid = Column(Float)
    cand_ask = Column(Float)
    cand_lastPrice = Column(Float)
    cand_open = Column(Float)
    cand_close = Column(Float)
    cand_avPriceDrop_Percent = Column(Float)
    cand_avPriceSpread_Percent = Column(Float)
    cand_targetPrice = Column(Float)
    cand_tipRank = Column(Integer)
    cand_updated = Column(DateTime)

    order_price = Column(Float)
    order_quantity = Column(Integer)
    order_placed = Column(DateTime)
    buy_order_id = Column(Integer)
    buy_last_fill_price=Column(Float)

    deal_lastStatus = Column(String)
    deal_statusUpdated = Column(DateTime)

    execution_time=Column(DateTime)
    execution_price=Column(Float)

    deal_isClosed = Column(Boolean)

def add_deal_to_db(candidate, price, orderVolume, addTime):
    engine = create_engine(DB_PATH)

    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    session = Session()
    d = Deal()
    d.stock=candidate["Stock"]
    d.cand_bid = candidate["Bid"]
    d.cand_ask = candidate["Ask"]
    if candidate["LastPrice"]=='-':
        d.cand_lastPric=0
    else:
        d.cand_lastPrice = candidate["LastPrice"]
    if candidate["Open"]=='-':
        d.cand_open=0
    else:
        d.cand_open = candidate["Open"]
    if candidate["Close"]=='-':
        d.cand_close=0
    else:
        d.cand_close = candidate["Close"]
    d.cand_avPriceDrop_Percent = candidate["averagePriceDropP"]
    d.cand_avPriceSpread_Percent = candidate["averagePriceSpreadP"]
    d.cand_targetPrice = candidate["target_price"]
    d.cand_tipRank = candidate["tipranksRank"]
    d.cand_updated = candidate["LastUpdate"]
    d.order_price = price
    d.order_quantity = orderVolume
    d.order_placed = addTime
    d.deal_lastStatus = "created by Algo Trader"
    d.deal_statusUpdated = addTime
    d.deal_isClosed = False
    d.buy_order_id=0

    session.add(d)
    session.commit()
    Session.remove()


def update_deal_in_db_by_order_status(orderId, status, lastfillprice):
    engine = create_engine(DB_PATH)

    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    session = Session()

    c = session.query(Deal).filter(Deal.buy_order_id ==orderId).all()
    if len(c)>0:

        c[-1].deal_lastStatus =status
        c[-1].deal_statusUpdated=datetime.datetime.now()
        c[-1].buy_last_fill_price=lastfillprice

    session.commit()
    Session.remove()

def update_deal_in_db_by_execution_details(contract, execution):
    engine = create_engine(DB_PATH)

    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    session = Session()

    c = session.query(Deal).filter(Deal.stock == contract.symbol).all()
    c[-1].buy_order_id =execution.orderId
    c[-1].deal_lastStatus ="confirmed tws"
    c[-1].execution_time=datetime.datetime.now()
    c[-1].execution_price=execution.price

    session.commit()
    Session.remove()





def checkDB():
    engine = create_engine(DB_PATH, echo=True)

    if path.exists('db.db'):
        pass
    else:
        Base.metadata.create_all(engine)
