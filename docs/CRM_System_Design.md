# WealthAI CRM System 設計書

## 📋 システム概要

### システム名
**WealthAI CRM System** - 顧客関係管理システム

### 目的
- 金融サービス顧客の包括的管理
- 保有商品・取引履歴の追跡
- 営業活動の記録・管理
- Amazon Bedrock AI チャット機能

## 🏗️ アーキテクチャ

### 技術スタック
- **Backend**: Python 3.9+, FastAPI
- **Frontend**: HTML5, JavaScript ES6+, Bootstrap 5
- **Database**: PostgreSQL (wealthai DB)
- **AI**: Amazon Bedrock Claude 3 Sonnet
- **Deployment**: systemd, Nginx reverse proxy

### サービス構成
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Nginx Proxy   │    │  FastAPI App    │
│                 │◄──►│   (/crm/)       │◄──►│   (Port 8000)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │ PostgreSQL DB   │
                                               │  (wealthai)     │
                                               └─────────────────┘
```

## 🗄️ データベース設計

### 主要テーブル
```sql
-- 営業担当者
sales_representatives (
    rep_id SERIAL PRIMARY KEY,
    rep_code VARCHAR(20) UNIQUE,
    name VARCHAR(100),
    department VARCHAR(50),
    branch VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    hire_date DATE
)

-- 顧客情報
customers (
    customer_id SERIAL PRIMARY KEY,
    customer_code VARCHAR(20) UNIQUE,
    name VARCHAR(100),
    name_kana VARCHAR(100),
    birth_date DATE,
    gender VARCHAR(10),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    occupation VARCHAR(50),
    annual_income BIGINT,
    risk_tolerance VARCHAR(20),
    investment_experience VARCHAR(20),
    sales_rep_id INTEGER REFERENCES sales_representatives(rep_id)
)

-- 保有商品
holdings (
    holding_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    product_id INTEGER,
    quantity INTEGER,
    purchase_price DECIMAL(15,2),
    purchase_date DATE,
    current_price DECIMAL(15,2),
    unrealized_gain_loss DECIMAL(15,2),
    realized_gain_loss DECIMAL(15,2)
)

-- 営業メモ
sales_notes (
    note_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    sales_rep_id INTEGER REFERENCES sales_representatives(rep_id),
    note_type VARCHAR(50),
    title VARCHAR(200),
    content TEXT,
    follow_up_date DATE,
    priority VARCHAR(20),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### データ統計（2025-09-05現在）
- **営業担当者**: 7名
- **顧客**: 18名（個人16名・法人2名）
- **保有商品**: 38件
- **営業メモ**: 26件

## 🎯 機能仕様

### 1. 顧客管理機能
- **顧客一覧表示**: ページネーション対応
- **顧客詳細表示**: 基本情報・保有商品・営業履歴
- **顧客検索**: 名前・コード・担当者での検索
- **顧客登録・編集**: フォーム入力・バリデーション

### 2. 保有商品管理
- **保有状況一覧**: 顧客別・商品別表示
- **損益計算**: 未実現・実現損益の自動計算
- **ポートフォリオ分析**: リスク分散状況表示

### 3. 営業メモ管理
- **メモ一覧**: 顧客別・担当者別表示
- **メモ作成・編集**: リッチテキスト対応
- **フォローアップ管理**: 期日管理・アラート機能
- **優先度管理**: 高・中・低の3段階

### 4. AI チャット機能
- **Bedrock統合**: Claude 3 Sonnet モデル使用
- **顧客情報連携**: 顧客データを考慮した回答
- **営業支援**: 商品提案・リスク分析

## 🎨 UI/UX設計

### メニュー構成
```
┌─────────────────────────────────────────┐
│  WealthAI CRM System                    │
├─────────────────────────────────────────┤
│  🏠 ダッシュボード                        │
│  👥 顧客一覧                             │
│  💼 保有商品                             │
│  📝 営業メモ                             │
│  🤖 AI チャット                          │
└─────────────────────────────────────────┘
```

### レスポンシブ対応
- **デスクトップ**: フル機能表示
- **タブレット**: 最適化されたレイアウト
- **モバイル**: コンパクト表示・タッチ操作対応

## 🔧 API仕様

### エンドポイント一覧
```
GET  /                     # ダッシュボード
GET  /customers            # 顧客一覧
GET  /customers/{id}       # 顧客詳細
POST /customers            # 顧客登録
PUT  /customers/{id}       # 顧客更新

GET  /holdings             # 保有商品一覧
GET  /holdings/customer/{id} # 顧客別保有商品

GET  /sales-notes          # 営業メモ一覧
POST /sales-notes          # 営業メモ作成
PUT  /sales-notes/{id}     # 営業メモ更新

POST /chat                 # AI チャット
GET  /api/stats            # 統計情報
```

## 🚀 デプロイメント

### systemd設定
```ini
[Unit]
Description=WealthAI CRM System
After=network.target postgresql.service

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/wealthai
ExecStart=/usr/bin/python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 環境設定
```bash
# .env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wealthai
DB_USER=wealthai_user
DB_PASSWORD=wealthai123

PRODUCT_MASTER_URL=http://localhost:8001
PRODUCT_MASTER_TOKEN=demo-token-12345

DEBUG=True
```

## 📊 パフォーマンス

### 目標値
- **レスポンス時間**: 平均 < 500ms
- **同時接続数**: 100ユーザー
- **稼働率**: 99.9%

### 最適化施策
- **データベース**: インデックス最適化
- **キャッシュ**: Redis導入検討
- **CDN**: 静的ファイル配信最適化

## 🔒 セキュリティ

### 認証・認可
- **セッション管理**: HTTPSセッション
- **入力検証**: SQLインジェクション対策
- **XSS対策**: テンプレートエスケープ

### データ保護
- **個人情報**: 暗号化保存
- **アクセスログ**: 監査証跡
- **バックアップ**: 定期自動バックアップ

## 🧪 テスト戦略

### テスト種別
- **単体テスト**: pytest使用
- **統合テスト**: API エンドポイント
- **E2Eテスト**: Selenium使用
- **負荷テスト**: Locust使用

## 📈 監視・運用

### ログ管理
```bash
# アプリケーションログ
journalctl -u wealthai-crm -f

# アクセスログ
tail -f /var/log/nginx/access.log | grep crm
```

### ヘルスチェック
```bash
# サービス状態確認
systemctl is-active wealthai-crm

# エンドポイント確認
curl -s http://localhost:8000/api/health
```

## 🔄 今後の拡張計画

### 短期（1-3ヶ月）
- **レポート機能**: 売上・顧客分析
- **通知機能**: メール・SMS通知
- **モバイルアプリ**: PWA対応

### 中期（3-6ヶ月）
- **ワークフロー**: 承認プロセス
- **API拡張**: 外部システム連携
- **AI強化**: より高度な分析機能

### 長期（6ヶ月以降）
- **マイクロサービス化**: サービス分離
- **リアルタイム**: WebSocket対応
- **機械学習**: 予測分析機能

---

**Document Version**: v1.0.0  
**Repository**: https://github.com/takehig/WealthAI-CRM  
**Last Updated**: 2025-09-05
