#!/usr/bin/env python3
"""
WealthAI データインポートスクリプト
CSVファイルからPostgreSQLデータベースにサンプルデータをインポートする
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import os
from pathlib import Path
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# データベース接続設定
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'crm'),
    'user': os.getenv('DB_USER', 'crm_user'),
    'password': os.getenv('DB_PASSWORD', 'crm123'),
    'port': int(os.getenv('DB_PORT', 5432))
}

def get_db_connection():
    """データベース接続を取得"""
    return psycopg2.connect(**DB_CONFIG)

def import_csv_to_table(csv_file_path, table_name, columns=None):
    """CSVファイルをテーブルにインポート"""
    try:
        # CSVファイルを読み込み
        df = pd.read_csv(csv_file_path)
        print(f"Loading {csv_file_path} -> {table_name} ({len(df)} rows)")
        
        # データベース接続
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # カラム名を指定されていない場合はCSVのヘッダーを使用
        if columns is None:
            columns = list(df.columns)
        
        # データをタプルのリストに変換（NaNをNoneに変換）
        data_tuples = []
        for row in df.values:
            # NaNをNoneに変換
            converted_row = []
            for value in row:
                if pd.isna(value):
                    converted_row.append(None)
                else:
                    converted_row.append(value)
            data_tuples.append(tuple(converted_row))
        
        # プレースホルダーを作成
        placeholders = ','.join(['%s'] * len(columns))
        columns_str = ','.join(columns)
        
        # INSERT文を実行
        insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES %s"
        execute_values(cursor, insert_query, data_tuples)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Successfully imported {len(df)} rows to {table_name}")
        
    except Exception as e:
        print(f"❌ Error importing {csv_file_path}: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

def main():
    """メイン処理"""
    # プロジェクトルートディレクトリを取得
    project_root = Path(__file__).parent.parent.parent
    csv_dir = project_root / "data" / "csv"
    
    print("🚀 Starting data import process...")
    print(f"Database: {DB_CONFIG['user']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    # インポート順序（外部キー制約を考慮）
    import_order = [
        ("sales_representatives.csv", "sales_representatives"),
        ("customers.csv", "customers"),
        ("products.csv", "products"),
        ("holdings.csv", "holdings"),
        ("sales_notes.csv", "sales_notes"),
        ("cash_inflows.csv", "cash_inflows"),
        ("economic_events.csv", "economic_events"),
    ]
    
    for csv_file, table_name in import_order:
        csv_path = csv_dir / csv_file
        if csv_path.exists():
            import_csv_to_table(csv_path, table_name)
        else:
            print(f"⚠️  CSV file not found: {csv_path}")
    
    print("✨ Data import process completed!")

if __name__ == "__main__":
    main()
