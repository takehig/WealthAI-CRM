# WealthAI AWS移行計画

## 移行概要
ローカル環境で動作するWealthAI CRMシステムをAWS環境に移行

## AWS構成案

### Option 1: シンプル構成（推奨）
```
Internet Gateway
    ↓
Application Load Balancer (ALB)
    ↓
EC2 Instance (t3.medium)
    - FastAPI アプリケーション
    - PostgreSQL (ローカルインストール)
    - Nginx (リバースプロキシ)
```

### Option 2: マネージドサービス構成
```
Internet Gateway
    ↓
Application Load Balancer (ALB)
    ↓
ECS Fargate
    - FastAPI コンテナ
    ↓
RDS PostgreSQL
```

### Option 3: サーバーレス構成
```
CloudFront
    ↓
API Gateway
    ↓
Lambda Functions
    ↓
RDS Serverless PostgreSQL
```

## 推奨構成: Option 1 (シンプル構成)

### 理由
- デモ用途に最適
- コスト効率が良い
- 管理が簡単
- 既存コードの変更が最小限

### AWS リソース

#### 1. VPC構成
- VPC: 10.0.0.0/16
- Public Subnet: 10.0.1.0/24 (ap-northeast-1a)
- Public Subnet: 10.0.2.0/24 (ap-northeast-1c) ※ALB用
- Internet Gateway
- Route Table

#### 2. セキュリティグループ
- **ALB Security Group**
  - Inbound: HTTP (80), HTTPS (443) from 0.0.0.0/0
  - Outbound: All traffic
- **EC2 Security Group**
  - Inbound: HTTP (8000) from ALB Security Group
  - Inbound: SSH (22) from 管理者IP
  - Outbound: All traffic

#### 3. EC2インスタンス
- **インスタンスタイプ**: t3.medium
- **AMI**: Ubuntu 24.04 LTS
- **ストレージ**: 20GB gp3
- **キーペア**: wealthai-keypair

#### 4. Application Load Balancer
- **スキーム**: Internet-facing
- **リスナー**: HTTP:80 → EC2:8000
- **ヘルスチェック**: /

#### 5. Route 53 (オプション)
- ドメイン設定（必要に応じて）

## 移行手順

### Phase 1: AWS基盤構築
1. VPC・サブネット作成
2. セキュリティグループ作成
3. キーペア作成
4. EC2インスタンス起動
5. ALB作成・設定

### Phase 2: アプリケーション移行
1. EC2にアプリケーション環境構築
2. PostgreSQLインストール・設定
3. アプリケーションコード配置
4. Nginx設定
5. systemdサービス設定

### Phase 3: データ移行
1. ローカルDBからデータエクスポート
2. AWS EC2のPostgreSQLにインポート
3. 動作確認

### Phase 4: 本番化設定
1. SSL証明書設定 (Let's Encrypt)
2. ドメイン設定
3. バックアップ設定
4. モニタリング設定

## 必要なファイル

### 1. Dockerfile (将来のコンテナ化用)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
COPY templates/ ./templates/
COPY static/ ./static/
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. nginx.conf
```nginx
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. systemd service file
```ini
[Unit]
Description=WealthAI FastAPI app
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/wealthai
Environment=PATH=/home/ubuntu/wealthai/venv/bin
ExecStart=/home/ubuntu/wealthai/venv/bin/uvicorn src.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## コスト見積もり

### 月額コスト (東京リージョン)
- EC2 t3.medium: ~$30
- ALB: ~$20
- EBS 20GB: ~$2
- データ転送: ~$5
- **合計**: ~$57/月

## セキュリティ考慮事項
- SSH接続は管理者IPのみ許可
- データベースは外部アクセス不可
- ALBでHTTPS終端
- 定期的なセキュリティアップデート

## 次のアクション
1. AWS CLI設定確認
2. VPC・EC2作成
3. アプリケーション移行
4. 動作確認
