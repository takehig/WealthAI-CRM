"""
データベース管理システム v2.0.0
Port: 8006
機能: 複数データベース対応SQL実行、データベース管理、メンテナンス
"""

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import logging
import json
from typing import List, Dict, Any
from datetime import datetime
import uvicorn

from config import DATABASES, SERVER_CONFIG

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=SERVER_CONFIG["title"], version=SERVER_CONFIG["version"])

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# テンプレート設定
templates = Jinja2Templates(directory="templates")

def get_db_connection(database_key: str):
    """指定されたデータベースへの接続を取得"""
    if database_key not in DATABASES:
        raise HTTPException(status_code=400, detail=f"Invalid database: {database_key}")
    
    db_config = DATABASES[database_key]
    try:
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed for {database_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """メイン画面"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "databases": DATABASES,
        "version": SERVER_CONFIG["version"]
    })

@app.post("/api/execute")
async def execute_sql(database: str = Form(...), query: str = Form(...)):
    """SQL実行API"""
    try:
        # データベース接続
        conn = get_db_connection(database)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # クエリ実行
        start_time = time.time()
        cursor.execute(query)
        execution_time = time.time() - start_time
        
        # 結果取得
        if cursor.description:
            # SELECT系クエリ
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            # 辞書形式に変換
            data = []
            for row in results:
                data.append(dict(row))
                
            response = {
                "status": "success",
                "type": "select",
                "columns": columns,
                "data": data,
                "row_count": len(data),
                "execution_time": round(execution_time, 3),
                "database": DATABASES[database]['name']
            }
        else:
            # INSERT/UPDATE/DELETE系クエリ
            conn.commit()
            response = {
                "status": "success", 
                "type": "modify",
                "affected_rows": cursor.rowcount,
                "execution_time": round(execution_time, 3),
                "database": DATABASES[database]['name']
            }
            
        cursor.close()
        conn.close()
        
        return response
        
    except Exception as e:
        logger.error(f"SQL execution error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "database": DATABASES.get(database, {}).get('name', database)
        }

@app.get("/api/tables/{database}")
async def get_tables(database: str):
    """テーブル一覧取得API"""
    try:
        conn = get_db_connection(database)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT table_name, table_type
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "tables": [dict(table) for table in tables],
            "database": DATABASES[database]['name']
        }
        
    except Exception as e:
        logger.error(f"Tables fetch error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/api/schema/{database}/{table}")
async def get_table_schema(database: str, table: str):
    """テーブルスキーマ取得API"""
    try:
        conn = get_db_connection(database)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table,))
        
        columns = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "columns": [dict(col) for col in columns],
            "table": table,
            "database": DATABASES[database]['name']
        }
        
    except Exception as e:
        logger.error(f"Schema fetch error: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@app.get("/health")
async def health():
    """ヘルスチェック"""
    return {
        "status": "healthy",
        "service": "Database-Management",
        "version": SERVER_CONFIG["version"],
        "databases": list(DATABASES.keys())
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=SERVER_CONFIG["port"])
