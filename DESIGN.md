# WealthAI-CRM システム設計書

## 📋 プロジェクト概要
**顧客管理・Bedrock チャット機能統合システム**

### 🎯 システム目的
- 顧客情報の包括的管理
- Amazon Bedrock Claude 3 Sonnet との AI チャット機能
- 金融商品販売における顧客対応支援

## 🏗️ システム構成

### 📊 基本情報
- **リポジトリ**: https://github.com/takehig/WealthAI-CRM
- **サービスポート**: 8000
- **アクセスURL**: http://44.217.45.24/crm/
- **技術スタック**: Python FastAPI, HTML5, Bootstrap 5

### 🔧 ファイル構造
```
WealthAI-CRM/
├── src/
│   ├── main.py              # FastAPI メインアプリケーション
│   ├── bedrock_client.py    # Amazon Bedrock 統合
│   └── database.py          # データベース接続
├── templates/
│   ├── index.html           # メイン画面
│   ├── customers.html       # 顧客管理画面
│   └── chat.html           # AI チャット画面
├── static/
│   ├── css/                # スタイルシート
│   └── js/                 # JavaScript
└── requirements.txt        # Python 依存関係
```

## 🔑 主要機能

### ✅ 実装済み機能
1. **顧客管理機能**
   - 顧客情報 CRUD 操作
   - 顧客検索・フィルタリング
   - 顧客履歴管理

2. **AI チャット機能**
   - Amazon Bedrock Claude 3 Sonnet 統合
   - リアルタイム AI 対話
   - チャット履歴保存

3. **統合ダッシュボード**
   - 顧客統計表示
   - チャット利用状況
   - システム状態監視

### 🔧 API エンドポイント
```
GET  /                    # メイン画面
GET  /customers          # 顧客管理画面
GET  /chat              # AI チャット画面
GET  /api/customers     # 顧客一覧取得
POST /api/customers     # 顧客作成
PUT  /api/customers/{id} # 顧客更新
GET  /api/chat          # チャット履歴取得
POST /api/chat          # AI チャット実行
```

## 🗄️ データベース設計

### 📊 テーブル構成
```sql
-- 顧客テーブル
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- チャット履歴テーブル
CREATE TABLE chat_history (
    chat_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔐 セキュリティ・認証

### 🛡️ 実装済みセキュリティ
- **IAM ロール**: takehig-DefaultEC2Role
- **Bedrock アクセス**: IAM ベース認証
- **CORS 設定**: 適切なオリジン制限
- **入力検証**: SQL インジェクション対策

## 🚀 デプロイ・運用

### 📦 systemd サービス
```ini
[Unit]
Description=WealthAI CRM Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/CRM/src
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 🔄 運用コマンド
```bash
# サービス管理
sudo systemctl start wealthai-crm
sudo systemctl stop wealthai-crm
sudo systemctl restart wealthai-crm
sudo systemctl status wealthai-crm

# ログ確認
sudo journalctl -u wealthai-crm -f
```

## 📈 パフォーマンス・監視

### 📊 監視項目
- **レスポンス時間**: API 応答速度
- **Bedrock 利用量**: AI チャット使用状況
- **データベース接続**: 接続プール状態
- **エラー率**: システムエラー発生頻度

## 🔮 今後の拡張予定

### 📋 計画中機能
1. **顧客セグメンテーション**: AI による顧客分析
2. **商品推奨機能**: ProductMaster 連携
3. **レポート機能**: 顧客分析レポート生成
4. **通知機能**: 重要イベント通知

## 📝 更新履歴
- **2025-09-13**: 設計書作成・現在の実装状況反映
- **2025-08-30**: システム統合完了
- **2025-08-28**: プロジェクト開始
