from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class ROIData(Base):
    __tablename__ = "roi_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    page_type = Column(String, index=True)  # 'geral', 'instagram', 'grupo'
    spend = Column(Float)
    sales = Column(Float)
    roi = Column(Float)
    period = Column(String)  # 'hourly', 'daily'

class SalesData(Base):
    __tablename__ = "sales_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    date = Column(String)
    total_orders = Column(Integer)
    total_numbers = Column(Integer)
    total_value = Column(Float)

class AffiliateData(Base):
    __tablename__ = "affiliate_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    affiliate_code = Column(String, index=True)
    affiliate_name = Column(String)
    total_paid_orders = Column(Float)
    order_count = Column(Integer)
    average_ticket = Column(Float)

class FacebookAdsData(Base):
    __tablename__ = "facebook_ads_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=func.now())
    account_id = Column(String, index=True)
    spend = Column(Float)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)