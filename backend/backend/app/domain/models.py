from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean
from app.infrastructure.db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True) # Telegram User ID
    telegram_username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    role = Column(String, default="GUEST") # GUEST, RESIDENT, VIP
    tenant_id = Column(String, default="Appex_Main")
    created_at = Column(DateTime, default=datetime.utcnow)

class Session(Base):
    __tablename__ = "schedule_sessions"
    
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, default="Appex_Main")
    date = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    title = Column(String)
    speaker_name = Column(String)
    speaker_role = Column(String, nullable=True)
    location = Column(String)

class Participant(Base):
    __tablename__ = "participants"
    
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, default="Appex_Main")
    full_name = Column(String)
    role = Column(String)
    bio = Column(String)
    telegram_username = Column(String, nullable=True)
    telegram_user_id = Column(Integer, nullable=True)

class RealEstateLot(Base):
    __tablename__ = "real_estate_lots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, default="Appex_Main")
    source = Column(String)
    title = Column(String)
    price_usd = Column(Float)
    predicted_roi = Column(Float, default=0.0)
    image_url = Column(String)
    address = Column(String, nullable=True)
    cadastral_number = Column(String, nullable=True)
    area_sqm = Column(Float, nullable=True)
    status = Column(String, nullable=True)
    auction_start_date = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
