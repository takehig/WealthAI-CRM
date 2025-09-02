"""
データベース管理システム
Port: 8006
機能: SQL実行、データベース管理、メンテナンス
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
import time
from typing import List, Dict, Any
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

# リクエストモデル
class QueryRequest(BaseModel):
    query: str

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
    """データベース管理UI"""
    return """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>データベース管理システム</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h1>データベース管理システム</h1>
            
            <div class="row mt-4">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h5>SQL実行</h5>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label for="sqlQuery" class="form-label">SQLクエリ</label>
                                <textarea class="form-control" id="sqlQuery" rows="5" placeholder="SELECT * FROM products LIMIT 10;"></textarea>
                            </div>
                            <button class="btn btn-primary" onclick="executeQuery()">実行</button>
                            <button class="btn btn-secondary ms-2" onclick="clearQuery()">クリア</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h5>実行結果</h5>
                        </div>
                        <div class="card-body">
                            <div id="queryResult">
                                <p class="text-muted">クエリを実行すると結果がここに表示されます</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            async function executeQuery() {
                const query = document.getElementById('sqlQuery').value.trim();
                if (!query) {
                    alert('SQLクエリを入力してください');
                    return;
                }
                
                try {
                    const response = await fetch('/api/execute-sql', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            sql: query,
                            params: []
                        })
                    });
                    
                    const result = await response.json();
                    displayResult(result);
                } catch (error) {
                    displayError('実行エラー: ' + error.message);
                }
            }
            
            function displayResult(result) {
                const resultDiv = document.getElementById('queryResult');
                
                if (result.status === 'error') {
                    resultDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <strong>エラー:</strong> ${result.error}
                        </div>
                    `;
                    return;
                }
                
                if (result.results && result.results.length > 0) {
                    const table = createTable(result.results);
                    resultDiv.innerHTML = `
                        <div class="alert alert-success">
                            <strong>成功:</strong> ${result.count}件の結果
                        </div>
                        ${table}
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="alert alert-info">
                            <strong>完了:</strong> ${result.message || 'クエリが正常に実行されました'}
                        </div>
                    `;
                }
            }
            
            function createTable(data) {
                if (!data || data.length === 0) return '<p>データがありません</p>';
                
                const headers = Object.keys(data[0]);
                let html = '<div class="table-responsive"><table class="table table-striped table-sm">';
                
                // ヘッダー
                html += '<thead><tr>';
                headers.forEach(header => {
                    html += `<th>${header}</th>`;
                });
                html += '</tr></thead>';
                
                // データ
                html += '<tbody>';
                data.forEach(row => {
                    html += '<tr>';
                    headers.forEach(header => {
                        html += `<td>${row[header] || ''}</td>`;
                    });
                    html += '</tr>';
                });
                html += '</tbody></table></div>';
                
                return html;
            }
            
            function displayError(message) {
                document.getElementById('queryResult').innerHTML = `
                    <div class="alert alert-danger">
                        ${message}
                    </div>
                `;
            }
            
            function clearQuery() {
                document.getElementById('sqlQuery').value = '';
                document.getElementById('queryResult').innerHTML = '<p class="text-muted">クエリを実行すると結果がここに表示されます</p>';
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/execute-sql")
async def execute_sql(request: dict):
    """SQL実行API"""
    try:
        sql = request.get("sql", "").strip()
        params = request.get("params", [])
        
        if not sql:
            return {"status": "error", "error": "SQLクエリが空です"}
        
        logger.info(f"[DATABASE] Executing SQL: {sql}")
        logger.info(f"[DATABASE] Parameters: {params}")
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
            
        if sql.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            result_data = [dict(row) for row in results]
            logger.info(f"[DATABASE] Query returned {len(result_data)} rows")
            conn.close()
            return {
                "status": "success",
                "query": sql,
                "params": params,
                "count": len(result_data),
                "results": result_data
            }
        else:
            conn.commit()
            conn.close()
            return {
                "status": "success", 
                "query": sql,
                "params": params,
                "message": "クエリが正常に実行されました"
            }
            
    except Exception as e:
        logger.error(f"[DATABASE] SQL execution error: {e}")
        return {
            "status": "error",
            "query": sql,
            "params": params,
            "error": str(e)
        }

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """データベース管理画面を表示"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.post("/execute")
async def execute_query(request: QueryRequest):
    """SQLクエリを実行"""
    start_time = time.time()
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="wealthai",
            user="wealthai_user",
            password="wealthai123",
            port=5432
        )
        
        cursor = conn.cursor()
        cursor.execute(request.query)
        
        # SELECT文の場合は結果を取得
        if request.query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            # 辞書形式に変換
            data = []
            for row in results:
                data.append(dict(zip(columns, row)))
            
            execution_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                "success": True,
                "data": data,
                "execution_time": execution_time,
                "message": f"{len(data)}件のレコードを取得しました"
            }
        else:
            # INSERT/UPDATE/DELETE等の場合
            conn.commit()
            execution_time = round((time.time() - start_time) * 1000, 2)
            
            return {
                "success": True,
                "data": [],
                "execution_time": execution_time,
                "message": f"クエリが正常に実行されました（影響行数: {cursor.rowcount}）"
            }
            
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return {
            "success": False,
            "error": str(e),
            "error_detail": error_detail,
            "execution_time": round((time.time() - start_time) * 1000, 2)
        }
    finally:
        if 'conn' in locals():
            conn.close()

@app.get("/health")
async def health_check():
    """ヘルスチェック"""
    return {"status": "healthy", "service": "Database Management", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
