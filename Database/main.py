"""
データベース管理システム
Port: 8006
機能: SQL実行、データベース管理、メンテナンス
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import time
import logging
import json
from typing import List, Dict, Any
from datetime import datetime

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

app = FastAPI(title="Database Management System", version="1.0.0")

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

def log_and_collect(message: str, logs: list):
    """OSログ出力とレスポンス用ログ収集を同時実行"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[DATABASE] {message}"
    
    # OSログ出力
    logger.info(log_message)
    
    # レスポンス用ログ収集
    logs.append(f"[{timestamp}] {message}")
    
    return log_message

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """データベース接続"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="crm_db", 
            user="crm_user",
            password="crm_password"
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

@app.get("/", response_class=HTMLResponse)
async def database_management_ui():
    """データベース管理画面を表示"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/execute")
async def execute_query(request: Request):
    """SQLクエリを実行"""
    start_time = time.time()
    logs = []
    
    try:
        # 生のリクエストボディを取得
        raw_body = await request.body()
        log_and_collect(f"Raw request received: {raw_body.decode()}", logs)
        
        # JSONパース
        data = json.loads(raw_body)
        log_and_collect(f"Parsed JSON: {data}", logs)
        
        # クエリ取得（queryまたはsqlフィールドに対応）
        query = data.get("query") or data.get("sql")
        if not query:
            log_and_collect("ERROR: No query field found", logs)
            return {
                "success": False,
                "error": "Query field required (query or sql)",
                "logs": logs
            }
        
        log_and_collect(f"Query execution started: {query}", logs)
        
        log_and_collect("Attempting database connection...", logs)
        log_and_collect("Host: localhost, Database: wealthai, User: wealthai_user", logs)
        
        conn = psycopg2.connect(
            host="localhost",
            database="wealthai",
            user="wealthai_user",
            password="wealthai123",
            port=5432
        )
        
        log_and_collect("✅ Database connection successful", logs)
        
        cursor = conn.cursor()
        log_and_collect(f"Executing query: {query}", logs)
        cursor.execute(query)
        
        # SELECT文の場合は結果を取得
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            log_and_collect(f"Found {len(results)} rows, {len(columns)} columns", logs)
            
            # 辞書形式に変換
            data = []
            for row in results:
                data.append(dict(zip(columns, row)))
            
            execution_time = round((time.time() - start_time) * 1000, 2)
            log_and_collect(f"Execution completed in {execution_time}ms", logs)
            
            return {
                "success": True,
                "data": data,
                "execution_time": execution_time,
                "message": f"{len(data)}件のレコードを取得しました",
                "logs": logs
            }
        else:
            # INSERT/UPDATE/DELETE等の場合
            conn.commit()
            execution_time = round((time.time() - start_time) * 1000, 2)
            log_and_collect(f"Transaction committed, affected rows: {cursor.rowcount}", logs)
            log_and_collect(f"Execution completed in {execution_time}ms", logs)
            
            return {
                "success": True,
                "data": [],
                "execution_time": execution_time,
                "message": f"クエリが正常に実行されました（影響行数: {cursor.rowcount}）",
                "logs": logs
            }
            
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        execution_time = round((time.time() - start_time) * 1000, 2)
        
        log_and_collect(f"❌ Exception occurred: {str(e)}", logs)
        log_and_collect(f"Error type: {type(e).__name__}", logs)
        log_and_collect(f"Execution failed after {execution_time}ms", logs)
        
        # OSログにもエラー詳細を出力
        logger.error(f"[DATABASE] SQL execution error: {str(e)}")
        logger.error(f"[DATABASE] Error detail: {error_detail}")
        
        return {
            "success": False,
            "error": str(e),
            "error_detail": error_detail,
            "execution_time": execution_time,
            "logs": logs
        }
    finally:
        if 'conn' in locals():
            conn.close()
            log_and_collect("Database connection closed", logs)

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "service": "Database Management", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
