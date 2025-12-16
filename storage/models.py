from sqlalchemy import Column, Integer, String, Float, DateTime
from storage.db import Base
from datetime import datetime

class Tick(Base):
    __tablename__ = "ticks"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    price = Column(Float)
    size = Column(Float)

class HourlySummary(Base):
    __tablename__ = "hourly_summary"
    ts = Column(DateTime, primary_key=True)  
    symbol1 = Column(String)
    symbol2 = Column(String)
    
    price_first = Column(Float)
    price_max = Column(Float)
    price_min = Column(Float)
    price_last = Column(Float)
    price_mean = Column(Float)
    price_std = Column(Float)
    
    spread_mean = Column(Float)
    spread_std = Column(Float)
    z_mean = Column(Float)
    z_max = Column(Float)
    
    corr_mean = Column(Float)
    corr_min = Column(Float)
    corr_max = Column(Float)
    corr_std = Column(Float)