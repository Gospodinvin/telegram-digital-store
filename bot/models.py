from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, BigInteger, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Creator(Base):
    __tablename__ = "creators"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_pro = Column(Boolean, default=False)
    pro_expires_at = Column(DateTime, nullable=True)
    balance_stars = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="creator")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey("creators.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price_stars = Column(Integer, nullable=False)
    file_id = Column(String(500), nullable=False)
    file_name = Column(String(200))
    file_size = Column(Integer)
    is_active = Column(Boolean, default=True)
    sales_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("Creator", back_populates="products")
    purchases = relationship("Purchase", back_populates="product")

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    buyer_telegram_id = Column(BigInteger, nullable=False)
    buyer_username = Column(String(100))
    price_paid = Column(Integer, nullable=False)
    commission = Column(Integer, nullable=False)
    creator_earned = Column(Integer, nullable=False)
    telegram_payment_id = Column(String(100))
    status = Column(String(20), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="purchases")

# Database setup
def init_db(database_url: str = "sqlite:///./store.db"):
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
