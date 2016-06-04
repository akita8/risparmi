from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


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
    tax_on_purchase_percentage = Column()
    account = Column(String)
    quantity = Column(Integer)
    buy_sell_price = Column(Float)
    dividend = Column(Float)
    commission = Column(Float)
    tax_percentage = Column(Float)
    exchange_rate = Column(Float)
    owner = Column(String)
    date_of_transaction = Column(DateTime)





engine = create_engine('sqlite:///prova.db', echo=True)
Base.metadata.bind=engine
Base.metadata.create_all(engine)

Session=sessionmaker(bind=engine)
session=Session()
