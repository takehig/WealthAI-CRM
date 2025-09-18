from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import psycopg2
from psycopg2.extras import RealDictCursor
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# データベース接続設定
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "crm_user",
    "password": "crm123",
    "database": "crm"
}

def get_db_connection():
    """データベース接続"""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """メインページ"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/execute-sql")
async def execute_sql(request: Request):
    """手動SQL実行"""
    try:
        data = await request.json()
        sql = data.get("sql", "").strip()
        
        if not sql:
            return {"status": "error", "error": "SQLクエリが空です"}
        
        connection = get_db_connection()
        if not connection:
            return {"status": "error", "error": "データベース接続エラー"}
        
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute(sql)
        
        # SELECT系のクエリの場合結果を取得
        if sql.upper().strip().startswith(("SELECT", "WITH", "SHOW")):
            results = cursor.fetchall()
            results_list = [dict(row) for row in results]
            connection.commit()
            connection.close()
            return {
                "status": "success",
                "results": results_list,
                "count": len(results_list)
            }
        else:
            # INSERT/UPDATE/DELETE系のクエリ
            connection.commit()
            affected_rows = cursor.rowcount
            connection.close()
            return {
                "status": "success",
                "message": f"{affected_rows}行が影響されました",
                "count": affected_rows
            }
            
    except Exception as e:
        if "connection" in locals():
            connection.rollback()
            connection.close()
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006)
