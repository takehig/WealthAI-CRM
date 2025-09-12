from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel

"""
WealthAI CRM データ参照アプリケーション
FastAPI + Jinja2 テンプレートを使用したWebアプリ
"""

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.database import get_db, Customer, SalesRepresentative, Product, Holding, SalesNote, CashInflow, EconomicEvent
from typing import List
import os
from pathlib import Path

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
    customers = db.query(Customer).join(SalesRepresentative).all()
    return templates.TemplateResponse("customers.html", {
        "request": request,
        "customers": customers
    })

@app.get("/api/customers")
async def get_customers_api(db: Session = Depends(get_db)):
    """顧客一覧API"""
    try:
        customers = db.query(Customer).join(SalesRepresentative).all()
        
        customer_list = []
        for customer in customers:
            customer_list.append({
                "customer_id": customer.customer_id,
                "customer_name": customer.customer_name,
                "email": customer.email,
                "phone": customer.phone,
                "address": customer.address,
                "registration_date": customer.registration_date.isoformat() if customer.registration_date else None,
                "customer_type": customer.customer_type,
                "risk_tolerance": customer.risk_tolerance,
                "sales_rep_name": customer.sales_representative.name if customer.sales_representative else None
            })
        
        return {
            "status": "success",
            "total_customers": len(customer_list),
            "customers": customer_list
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "customers": []
        }

@app.get("/customers/{customer_id}", response_class=HTMLResponse)
async def customer_detail(request: Request, customer_id: int, db: Session = Depends(get_db)):
    """顧客詳細"""
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        return templates.TemplateResponse("404.html", {"request": request})
    
    # 保有商品を取得
    holdings = db.query(Holding).join(Product).filter(Holding.customer_id == customer_id).all()
    
    # 営業メモを取得
    sales_notes = db.query(SalesNote).filter(SalesNote.customer_id == customer_id).order_by(SalesNote.created_at.desc()).all()
    
    # 入金予測を取得
    cash_inflows = db.query(CashInflow).filter(CashInflow.customer_id == customer_id).order_by(CashInflow.predicted_date).all()
    
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
    products = db.query(Product).all()
    return templates.TemplateResponse("holdings.html", {
        "request": request,
        "holdings": holdings,
        "customers": customers,
        "products": products
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
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # 更新データの適用
    update_data = customer_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    return customer

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

@app.get("/sales-notes", response_class=HTMLResponse)
async def sales_notes_list(request: Request, db: Session = Depends(get_db)):
    """営業メモ一覧"""
    sales_notes = db.query(SalesNote).join(Customer).join(SalesRepresentative).order_by(SalesNote.created_at.desc()).all()
    return templates.TemplateResponse("sales_notes.html", {
        "request": request,
        "sales_notes": sales_notes
    })

@app.get("/cash-inflows", response_class=HTMLResponse)
async def cash_inflows_list(request: Request, db: Session = Depends(get_db)):
    """入金予測一覧"""
    cash_inflows = db.query(CashInflow).join(Customer).order_by(CashInflow.predicted_date).all()
    return templates.TemplateResponse("cash_inflows.html", {
        "request": request,
        "cash_inflows": cash_inflows
    })

@app.get("/economic-events", response_class=HTMLResponse)
async def economic_events_list(request: Request, db: Session = Depends(get_db)):
    """経済イベント一覧"""
    events = db.query(EconomicEvent).order_by(EconomicEvent.event_date.desc()).all()
    return templates.TemplateResponse("economic_events.html", {
        "request": request,
        "events": events
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Bedrockチャット機能のインポート
from bedrock_chat import bedrock_chat_service
from pydantic import BaseModel
from fastapi import BackgroundTasks
from fastapi import BackgroundTasks
import asyncio

# チャットリクエストモデル
class ChatRequest(BaseModel):
    message: str
    customer_id: Optional[int] = None
    conversation_history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    usage: dict

# チャット関連エンドポイント
@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_bedrock(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Bedrockを使用したチャット機能
    """
    try:
        # 顧客コンテキストを取得
        customer_context = None
        if request.customer_id:
            customer = db.query(Customer).filter(Customer.customer_id == request.customer_id).first()
            if customer:
                customer_context = {
                    "name": customer.name,
                    "age": customer.age,
                    "investment_experience": customer.investment_experience,
                    "risk_tolerance": customer.risk_tolerance,
                    "total_assets": customer.total_assets
                }
        
        # Bedrockチャットサービスを呼び出し
        result = await bedrock_chat_service.chat(
            message=request.message,
            conversation_history=request.conversation_history,
            customer_context=customer_context
        )
        
        return ChatResponse(
            response=result["message"],
            timestamp=result["timestamp"],
            usage=result["usage"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat")
async def chat_page(request: Request):
    """
    チャットページを表示
    """
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/api/customers/{customer_id}/chat-context")
async def get_customer_chat_context(customer_id: int, db: Session = Depends(get_db)):
    """
    顧客のチャットコンテキスト情報を取得
    """
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # 顧客の保有資産情報も取得
        holdings = db.query(Holding).filter(Holding.customer_id == customer_id).all()
        total_holdings_value = sum([h.current_value for h in holdings if h.current_value])
        
        context = {
            "customer_id": customer.customer_id,
            "name": customer.name,
            "age": customer.age,
            "investment_experience": customer.investment_experience,
            "risk_tolerance": customer.risk_tolerance,
            "total_assets": customer.total_assets,
            "holdings_count": len(holdings),
            "total_holdings_value": total_holdings_value
        }
        
        return context
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 債券保有顧客リストアップ機能
@app.get("/api/customers/bond-holders")
async def get_bond_holding_customers(db: Session = Depends(get_db)):
    """
    満期保有債券を持つ顧客をリストアップ
    """
    try:
        # 債券を保有している顧客を取得
        bond_holders = db.query(Customer, Holding, Product).join(
            Holding, Customer.customer_id == Holding.customer_id
        ).join(
            Product, Holding.product_id == Product.product_id
        ).filter(
            Product.product_type == 'bond'
        ).all()
        
        # 顧客ごとにグループ化
        customer_bonds = {}
        for customer, holding, product in bond_holders:
            if customer.customer_id not in customer_bonds:
                customer_bonds[customer.customer_id] = {
                    'customer': {
                        'customer_id': customer.customer_id,
                        'name': customer.name,
                        'age': customer.age,
                        'total_assets': customer.total_assets,
                        'risk_tolerance': customer.risk_tolerance
                    },
                    'bonds': []
                }
            
            customer_bonds[customer.customer_id]['bonds'].append({
                'product_name': product.product_name,
                'product_code': product.product_code,
                'issuer': product.issuer,
                'maturity_date': product.maturity_date.strftime('%Y-%m-%d') if product.maturity_date else None,
                'interest_rate': float(product.interest_rate) if product.interest_rate else None,
                'quantity': holding.quantity,
                'current_value': holding.current_value,
                'purchase_date': holding.purchase_date.strftime('%Y-%m-%d') if holding.purchase_date else None
            })
        
        return {
            'total_customers': len(customer_bonds),
            'customers': list(customer_bonds.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"債券保有顧客の取得に失敗しました: {str(e)}")

@app.get("/bond-holders")
async def bond_holders_page(request: Request):
    """
    債券保有顧客一覧ページを表示
    """
    return templates.TemplateResponse("bond_holders.html", {"request": request})
