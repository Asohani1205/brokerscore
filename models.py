from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Broker(Base):
    __tablename__ = "brokers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    image_url = Column(String)
    qr_code_url = Column(String)
    score = Column(Integer, default=0)
    referrals = relationship("Referral", back_populates="broker")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contact_number = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    broker_id = Column(Integer, ForeignKey("brokers.id"))
    broker = relationship("Broker", back_populates="customers")

class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    broker_id = Column(Integer, ForeignKey("brokers.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    referral_date = Column(DateTime, default=datetime.utcnow)
    broker = relationship("Broker", back_populates="referrals")
    customer = relationship("Customer", back_populates="referrals")

# Add relationship to Broker model
Broker.customers = relationship("Customer", back_populates="broker")
Customer.referrals = relationship("Referral", back_populates="customer")

# Create database engine
SQLALCHEMY_DATABASE_URL = "sqlite:///./brokerscore.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create all tables
Base.metadata.create_all(bind=engine) 