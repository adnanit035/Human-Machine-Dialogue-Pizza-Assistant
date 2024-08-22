from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    order_number = Column(String, unique=True, nullable=False)
    order_list = Column(JSON, nullable=False)
    total_price = Column(Float, nullable=False)
    preparation_time = Column(Integer, nullable=False)
    pickup_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database configuration
DATABASE_URL = "sqlite:///orders.db"  # Update this with your database URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)
