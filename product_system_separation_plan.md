# 商品情報システム分離計画

## 目的
エージェントが複数システムを横断する動作を実現するため、商品情報を独立したシステムとして分離する。

## 現在の構成
- **メインCRMシステム**: WealthAI（顧客管理・営業支援）
- **商品情報**: 現在はCRM内のproductsテーブルに格納

## 分離後の構成

### 1. メインCRMシステム（既存）
- **URL**: http://57.183.66.123/
- **機能**: 顧客管理、営業メモ、入金予測、保有商品管理
- **データベース**: 商品情報以外の全テーブル

### 2. 商品情報システム（新規作成）
- **名称**: ProductMaster System
- **機能**: 商品マスター管理（登録・参照・更新）
- **独立したフロントエンド**: 商品管理専用UI
- **独立したバックエンド**: 商品情報API
- **データベース**: 商品情報専用テーブル

## 技術仕様

### 商品情報システム
- **フロントエンド**: React + TypeScript + Bootstrap
- **バックエンド**: FastAPI + PostgreSQL
- **デプロイ**: 別のEC2インスタンス or 同一インスタンスの別ポート
- **API**: RESTful API（商品検索・詳細取得・登録・更新）

### システム間連携
- **CRMシステム**: 商品情報システムのAPIを呼び出し
- **認証**: API Key または JWT トークン
- **データ同期**: リアルタイムAPI呼び出し

## 実装ステップ

### Phase 1: 商品情報システム構築
1. 商品情報システム用ディレクトリ作成
2. React + FastAPI環境構築
3. 商品データベース設計・構築
4. 商品管理API開発
5. 商品管理フロントエンド開発

### Phase 2: システム分離
1. 既存CRMから商品データ抽出
2. 商品情報システムにデータ移行
3. CRMシステムのAPI呼び出し実装
4. 動作確認・テスト

### Phase 3: デプロイ・統合
1. 商品情報システムのAWSデプロイ
2. システム間連携テスト
3. 本番環境での動作確認

## データ構造

### 商品情報システムのテーブル
```sql
-- 商品マスターテーブル（拡張版）
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_type VARCHAR(50) NOT NULL,
    currency VARCHAR(10) DEFAULT 'JPY',
    issuer VARCHAR(100),
    maturity_date DATE,
    interest_rate DECIMAL(5,4),
    risk_level INTEGER,
    minimum_investment BIGINT,
    commission_rate DECIMAL(5,4),
    description TEXT,
    features TEXT[],
    target_customer_type VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 商品カテゴリテーブル
CREATE TABLE product_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    parent_category_id INTEGER REFERENCES product_categories(category_id),
    description TEXT
);

-- 商品価格履歴テーブル
CREATE TABLE product_prices (
    price_id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(product_id),
    price DECIMAL(15,2) NOT NULL,
    price_date DATE NOT NULL,
    price_type VARCHAR(20) -- current, historical, projected
);
```

## API仕様

### 商品情報システム API
- `GET /api/products` - 商品一覧取得
- `GET /api/products/{product_id}` - 商品詳細取得
- `POST /api/products` - 商品登録
- `PUT /api/products/{product_id}` - 商品更新
- `DELETE /api/products/{product_id}` - 商品削除
- `GET /api/products/search` - 商品検索

### CRMシステムからの呼び出し
```python
# 商品情報取得例
async def get_product_info(product_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{PRODUCT_SYSTEM_URL}/api/products/{product_id}",
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )
        return response.json()
```

## 期待される効果

### エージェント動作の実現
1. **顧客情報**: CRMシステムから取得
2. **商品情報**: 商品情報システムから取得
3. **横断的な分析**: 複数システムの情報を統合

### デモシナリオ例
1. エージェントが顧客の満期債券を確認（CRMシステム）
2. 代替商品を検索（商品情報システム）
3. 顧客の投資方針と照合（CRMシステム）
4. 最適な商品を提案

## 次のアクション
1. 商品情報システムの詳細設計
2. 開発環境の準備
3. プロトタイプ開発開始

作成日時: 2025-08-21 08:40 UTC
