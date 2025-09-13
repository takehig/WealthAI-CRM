from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel
import requests

"""
WealthAI CRM データ参照アプリケーション
FastAPI + Jinja2 テンプレートを使用したWebアプリ
"""

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, Column, Integer, String, Date
from models.database import get_db, Customer, SalesRepresentative, Product, Holding, SalesNote, CashInflow, EconomicEvent, Base
from typing import List
import os
from pathlib import Path

# CRM商品モデル
class CRMProduct(Base):
    __tablename__ = "crm_products"
    id = Column(Integer, primary_key=True)
    product_code = Column(String(50), unique=True)
    product_name = Column(String(200))
    maturity_date = Column(Date)

# Pydantic モデル
class CustomerCreate(BaseModel):
    customer_code: str
    name: str
    name_kana: Optional[str] = None
    birth_date: Optional[date] = None
    occupation: Optional[str] = None
    annual_income: Optional[float] = None
    net_worth: Optional[float] = None
    risk_tolerance: Optional[int] = None
    investment_experience: Optional[str] = None
    sales_rep: Optional[str] = None

class CustomerUpdate(BaseModel):
    customer_code: Optional[str] = None
    name: Optional[str] = None
    name_kana: Optional[str] = None
    birth_date: Optional[date] = None
    occupation: Optional[str] = None
    annual_income: Optional[float] = None
    net_worth: Optional[float] = None
    risk_tolerance: Optional[int] = None
    investment_experience: Optional[str] = None
    sales_rep: Optional[str] = None

class HoldingCreate(BaseModel):
    customer_id: int
    product_id: int
    quantity: float
    purchase_price: float
    current_price: Optional[float] = None
    purchase_date: date
    maturity_date: Optional[date] = None

class HoldingUpdate(BaseModel):
    customer_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[float] = None
    purchase_price: Optional[float] = None
    current_price: Optional[float] = None
    purchase_date: Optional[date] = None
    maturity_date: Optional[date] = None

# FastAPIアプリケーション初期化
app = FastAPI(title="WealthAI CRM", description="ウェルスマネジメント向けCRMデータ参照システム")

# テンプレートとスタティックファイルの設定
BASE_DIR = Path(__file__).parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# スタティックファイルディレクトリを作成（存在しない場合）
static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """ダッシュボード - 全体概要"""
    
    # 基本統計情報を取得
    stats = {
        "total_customers": db.query(Customer).count(),
        "total_products": db.query(Product).count(),
        "total_holdings": db.query(Holding).count(),
        "total_sales_notes": db.query(SalesNote).count(),
        "total_cash_inflows": db.query(CashInflow).count(),
        "total_economic_events": db.query(EconomicEvent).count(),
    }
    
    # 保有資産総額を計算
    total_assets = db.query(func.sum(Holding.current_value)).scalar() or 0
    
    # 入金予測総額を計算
    total_predicted_inflows = db.query(func.sum(CashInflow.predicted_amount)).filter(
        CashInflow.status == 'predicted'
    ).scalar() or 0
    
    stats["total_assets"] = total_assets
    stats["total_predicted_inflows"] = total_predicted_inflows
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats
    })

@app.get("/customers", response_class=HTMLResponse)
async def customers_list(request: Request, db: Session = Depends(get_db)):
    """顧客一覧"""
    customers = db.query(Customer).all()
    return templates.TemplateResponse("customers.html", {
        "request": request,
        "customers": customers
    })

@app.get("/customers/{customer_id}", response_class=HTMLResponse)
async def customer_detail(request: Request, customer_id: int, db: Session = Depends(get_db)):
    """顧客詳細"""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        return templates.TemplateResponse("404.html", {"request": request})
    
    # 保有商品を取得
    holdings = db.query(Holding).join(Product).filter(Holding.customer_id == customer_id).all()
    
    # 営業メモを取得
    sales_notes = db.query(SalesNote).filter(SalesNote.customer_id == customer_id).all()
    
    # 入金予測を取得
    cash_inflows = db.query(CashInflow).filter(CashInflow.customer_id == customer_id).all()
    
    return templates.TemplateResponse("customer_detail.html", {
        "request": request,
        "customer": customer,
        "holdings": holdings,
        "sales_notes": sales_notes,
        "cash_inflows": cash_inflows
    })

@app.get("/holdings", response_class=HTMLResponse)
async def holdings_list(request: Request, db: Session = Depends(get_db)):
    """保有商品一覧"""
    holdings = db.query(Holding).join(Customer).join(Product).filter(Holding.status == 'active').all()
    customers = db.query(Customer).all()
    crm_products = db.query(CRMProduct).all()
    return templates.TemplateResponse("holdings.html", {
        "request": request,
        "holdings": holdings,
        "customers": customers,
        "products": crm_products
    })

@app.get("/products", response_class=HTMLResponse)
async def crm_products_list(request: Request, db: Session = Depends(get_db)):
    """CRM商品一覧"""
    crm_products = db.query(CRMProduct).all()
    return templates.TemplateResponse("crm_products.html", {
        "request": request,
        "products": crm_products
    })

# 顧客 CRUD API
@app.get("/api/customers")
async def get_customers_api(db: Session = Depends(get_db)):
    """顧客一覧API"""
    customers = db.query(Customer).all()
    return customers

@app.get("/api/customers/{customer_id}")
async def get_customer_api(customer_id: int, db: Session = Depends(get_db)):
    """顧客詳細API"""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.post("/api/customers")
async def create_customer_api(customer_data: CustomerCreate, db: Session = Depends(get_db)):
    """顧客作成API"""
    # 顧客コード重複チェック
    existing = db.query(Customer).filter(Customer.customer_code == customer_data.customer_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer code already exists")
    
    customer = Customer(**customer_data.dict())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

@app.put("/api/customers/{customer_id}")
async def update_customer_api(customer_id: int, customer_data: CustomerUpdate, db: Session = Depends(get_db)):
    """顧客更新API"""
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # 更新データの適用（リレーションフィールド除外）
        update_data = customer_data.dict(exclude_unset=True)
        
        # SQLAlchemyリレーションフィールドを除外
        relation_fields = ['sales_rep', 'holdings', 'sales_notes', 'cash_inflows']
        
        for field, value in update_data.items():
            # リレーションフィールドをスキップ
            if field in relation_fields:
                continue
                
            if hasattr(customer, field) and value is not None:
                # データ型変換処理
                if field == 'sales_rep_id' and isinstance(value, str):
                    # 外部キーは整数に変換（空文字列はNoneに）
                    value = int(value) if value.strip() else None
                elif field in ['annual_income', 'net_worth'] and isinstance(value, str):
                    # 数値フィールドは整数に変換（空文字列はNoneに）
                    value = int(value) if value.strip() else None
                elif field == 'risk_tolerance' and isinstance(value, str):
                    # リスク許容度のマッピング（UI値→DB値）
                    risk_mapping = {
                        '1': 'conservative',
                        '2': 'moderate_conservative', 
                        '3': 'moderate',
                        '4': 'moderate_aggressive',
                        '5': 'aggressive'
                    }
                    value = risk_mapping.get(value, value)
                elif field == 'investment_experience' and isinstance(value, str):
                    # 投資経験のマッピング（UI値→DB値）
                    experience_mapping = {
                        '初心者': 'beginner',
                        '経験者': 'experienced',
                        '上級者': 'expert'
                    }
                    value = experience_mapping.get(value, value)
                
                setattr(customer, field, value)
        
        db.commit()
        db.refresh(customer)
        return customer
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data type: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

# 保有商品 CRUD API
@app.get("/api/holdings")
async def get_holdings_api(db: Session = Depends(get_db)):
    """保有商品一覧API"""
    holdings = db.query(Holding).join(Customer).join(Product).all()
    return holdings

@app.get("/api/holdings/{holding_id}")
async def get_holding_api(holding_id: int, db: Session = Depends(get_db)):
    """保有商品詳細API"""
    holding = db.query(Holding).filter(Holding.holding_id == holding_id).first()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    return holding

@app.post("/api/holdings")
async def create_holding_api(holding_data: HoldingCreate, db: Session = Depends(get_db)):
    """保有商品作成API"""
    holding = Holding(**holding_data.dict())
    holding.status = 'active'
    holding.current_value = holding.quantity * (holding.current_price or holding.purchase_price)
    db.add(holding)
    db.commit()
    db.refresh(holding)
    return holding

@app.put("/api/holdings/{holding_id}")
async def update_holding_api(holding_id: int, holding_data: HoldingUpdate, db: Session = Depends(get_db)):
    """保有商品更新API"""
    holding = db.query(Holding).filter(Holding.holding_id == holding_id).first()
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    
    # 更新データの適用
    update_data = holding_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(holding, field, value)
    
    # 現在価値を再計算
    holding.current_value = holding.quantity * (holding.current_price or holding.purchase_price)
    
    db.commit()
    db.refresh(holding)
    return holding

# CRM商品 API
@app.get("/api/crm-products")
async def get_crm_products_api(db: Session = Depends(get_db)):
    """CRM商品一覧API"""
    crm_products = db.query(CRMProduct).all()
    return crm_products

@app.post("/api/sync-products")
async def sync_products_from_master(db: Session = Depends(get_db)):
    """ProductMasterから商品同期"""
    try:
        # ProductMaster APIから商品情報取得
        response = requests.get("http://localhost:8001/api/products")
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="ProductMaster API error")
        
        products_data = response.json()
        products = products_data.get("products", [])
        
        sync_count = 0
        for product in products:
            # 既存商品確認
            existing = db.query(CRMProduct).filter(
                CRMProduct.product_code == product["product_code"]
            ).first()
            
            if existing:
                # 更新
                existing.product_name = product["product_name"]
                existing.maturity_date = product.get("maturity_date")
            else:
                # 新規作成
                crm_product = CRMProduct(
                    product_code=product["product_code"],
                    product_name=product["product_name"],
                    maturity_date=product.get("maturity_date")
                )
                db.add(crm_product)
            sync_count += 1
        
        db.commit()
        return {"status": "success", "synced_count": sync_count}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync error: {str(e)}")

# 他のエンドポイント（省略）
@app.get("/sales-notes", response_class=HTMLResponse)
async def sales_notes_list(request: Request, db: Session = Depends(get_db)):
    """営業メモ一覧"""
    sales_notes = db.query(SalesNote).join(Customer).all()
    return templates.TemplateResponse("sales_notes.html", {
        "request": request,
        "sales_notes": sales_notes
    })

@app.get("/cash-inflows", response_class=HTMLResponse)
async def cash_inflows_list(request: Request, db: Session = Depends(get_db)):
    """入金予測一覧"""
    cash_inflows = db.query(CashInflow).join(Customer).all()
    return templates.TemplateResponse("cash_inflows.html", {
        "request": request,
        "cash_inflows": cash_inflows
    })

@app.get("/economic-events", response_class=HTMLResponse)
async def economic_events_list(request: Request, db: Session = Depends(get_db)):
    """経済イベント一覧"""
    economic_events = db.query(EconomicEvent).all()
    return templates.TemplateResponse("economic_events.html", {
        "request": request,
        "economic_events": economic_events
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
