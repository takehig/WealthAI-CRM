"""
WealthAI データベースモデル定義
SQLAlchemyを使用したORMモデル
"""

from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Boolean, DECIMAL, Text, ForeignKey, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TSVECTOR
import os
from dotenv import load_dotenv

load_dotenv()

# データベース接続設定
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 営業担当者モデル
class SalesRepresentative(Base):
    __tablename__ = "sales_representatives"
    
    rep_id = Column(Integer, primary_key=True, index=True)
    rep_code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(50))
    branch = Column(String(50))
    email = Column(String(100))
    phone = Column(String(20))
    hire_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    
    # リレーション
    customers = relationship("Customer", back_populates="sales_rep")

# 顧客モデル
class Customer(Base):
    __tablename__ = "customers"
    
    customer_id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_kana = Column(String(100))
    birth_date = Column(Date)
    gender = Column(String(10))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    occupation = Column(String(50))
    annual_income = Column(Integer)
    net_worth = Column(Integer)
    risk_tolerance = Column(String(20))
    investment_experience = Column(String(20))
    sales_rep_id = Column(Integer, ForeignKey("sales_representatives.rep_id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # リレーション
    sales_rep = relationship("SalesRepresentative", back_populates="customers")
    holdings = relationship("Holding", back_populates="customer")
    sales_notes = relationship("SalesNote", back_populates="customer")
    cash_inflows = relationship("CashInflow", back_populates="customer")

# 商品モデル
class Product(Base):
    __tablename__ = "products"
    
    product_id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), unique=True, nullable=False)
    product_name = Column(String(200), nullable=False)
    product_type = Column(String(50), nullable=False)
    currency = Column(String(10), default="JPY")
    issuer = Column(String(100))
    maturity_date = Column(Date)
    interest_rate = Column(DECIMAL(5,4))
    risk_level = Column(Integer)
    minimum_investment = Column(Integer)
    commission_rate = Column(DECIMAL(5,4))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # リレーション
    holdings = relationship("Holding", back_populates="product")

# 保有商品モデル
class Holding(Base):
    __tablename__ = "holdings"
    
    holding_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(DECIMAL(15,2), nullable=False)
    unit_price = Column(DECIMAL(15,2), nullable=False)
    purchase_date = Column(Date, nullable=False)
    current_price = Column(DECIMAL(15,2))
    current_value = Column(DECIMAL(15,2))
    unrealized_gain_loss = Column(DECIMAL(15,2))
    maturity_date = Column(Date)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # リレーション
    customer = relationship("Customer", back_populates="holdings")
    product = relationship("Product", back_populates="holdings")

# 営業メモモデル（シンプル化・雑メモ構造）
class SalesNote(Base):
    __tablename__ = "sales_notes"
    
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), primary_key=True)
    sales_rep_id = Column(Integer, ForeignKey("sales_representatives.rep_id"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    search_vector = Column(TSVECTOR)
    
    # リレーション
    customer = relationship("Customer", back_populates="sales_notes")
    sales_rep = relationship("SalesRepresentative")

# 入金予測モデル
class CashInflow(Base):
    __tablename__ = "cash_inflows"
    
    inflow_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"))
    source_type = Column(String(50))
    predicted_amount = Column(Integer, nullable=False)
    predicted_date = Column(Date, nullable=False)
    confidence_level = Column(String(20))
    source_note = Column(Text)
    actual_amount = Column(Integer)
    actual_date = Column(Date)
    status = Column(String(20), default="predicted")
    sales_rep_id = Column(Integer, ForeignKey("sales_representatives.rep_id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # リレーション
    customer = relationship("Customer", back_populates="cash_inflows")
    sales_rep = relationship("SalesRepresentative")

# 経済イベントモデル
class EconomicEvent(Base):
    __tablename__ = "economic_events"
    
    event_id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    event_date = Column(Date, nullable=False)
    impact_level = Column(String(20))
    affected_sectors = Column(ARRAY(Text))
    affected_currencies = Column(ARRAY(String(50)))
    created_at = Column(DateTime, server_default=func.now())

# データベースセッション取得関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
