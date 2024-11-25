from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class StoreStatus(Base):
    __tablename__ = "store_status"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, nullable=False, index=True)
    timestamp_utc = Column(DateTime, nullable=False, index=True)
    status = Column(String(10), nullable=False)

class BusinessHours(Base):
    __tablename__ = "business_hours"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, nullable=False, index=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time_local = Column(String(8), nullable=False)  # HH:MM:SS
    end_time_local = Column(String(8), nullable=False)    # HH:MM:SS

class StoreTimezone(Base):
    __tablename__ = "store_timezones"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, nullable=False, unique=True, index=True)
    timezone_str = Column(String(50), nullable=False)

class Report(Base):
    __tablename__ = "reports"
    id = Column(String(36), primary_key=True)  
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    file_path = Column(String(255), nullable=True)
    
