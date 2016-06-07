from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Date

Base = declarative_base()


class Bond(Base):

    __tablename__ = 'bond'

    id = Column(Integer, primary_key=True)
    symbol = Column(String, primary_key=True)
    denomination = Column(String)
    market = Column(String)
    sector = Column(String)
    currency = Column(String)
    isin = Column(String)
    nation = Column(String)
    transaction = Column(String)
    typology = Column(String)
    account = Column(String)
    quantity = Column(Integer)
    buy_sell_price = Column(Float)
    price_issued = Column(Float)
    coupon = Column(Float)
    commission = Column(Float)
    tax_percentage = Column(Float)
    exchange_rate = Column(Float)
    owner = Column(String)
    date_of_transaction = Column(Date)
    date_of_refund = Column(Date)
    date_of_issue = Column(Date)


class Stock(Base):

    __tablename__ = 'stock'

    id = Column(Integer, primary_key=True)
    symbol = Column(String, primary_key=True)
    denomination = Column(String)
    market = Column(String)
    sector = Column(String)
    currency = Column(String)
    isin = Column(String)
    nation = Column(String)
    transaction = Column(String)
    tax_on_purchase_percentage = Column(Float)
    account = Column(String)
    quantity = Column(Integer)
    buy_sell_price = Column(Float)
    dividend = Column(Float)
    commission = Column(Float)
    tax_percentage = Column(Float)
    exchange_rate = Column(Float)
    owner = Column(String)
    date_of_transaction = Column(Date)
