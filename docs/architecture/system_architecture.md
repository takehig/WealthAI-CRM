# WealthAI システム構成図

## 🏗️ 全体アーキテクチャ

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WealthAI CRM System                            │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────────┐
│   開発環境      │    │   デプロイ      │    │        AWS本番環境          │
│   (ローカル)    │    │   (S3経由)      │    │                             │
└─────────────────┘    └─────────────────┘    └─────────────────────────────┘
         │                       │                           │
         ▼                       ▼                           ▼

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────────┐
│ Windows WSL     │    │ S3 Bucket       │    │ EC2 Instance                │
│ Ubuntu 24.04    │    │ (Artifacts)     │    │ t3.medium                   │
│                 │    │                 │    │ Ubuntu 22.04                │
│ ├─ Python 3.10  │    │ ├─ Versioning   │    │                             │
│ ├─ PostgreSQL   │    │ ├─ Encryption   │    │ ├─ Nginx (Port 80)          │
│ ├─ FastAPI      │    │ └─ IAM Access   │    │ ├─ FastAPI (Port 8000)      │
│ └─ 68件データ   │    │                 │    │ ├─ PostgreSQL 14            │
└─────────────────┘    └─────────────────┘    │ ├─ systemd Service          │
                                              │ └─ 68件データ               │
                                              └─────────────────────────────┘
```

## 🌐 ネットワーク構成

```
Internet
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                        AWS VPC                                 │
│                     10.0.0.0/16                                │
│                                                                 │
│  ┌─────────────────┐              ┌─────────────────┐          │
│  │ Public Subnet   │              │ Public Subnet   │          │
│  │ 10.0.1.0/24     │              │ 10.0.2.0/24     │          │
│  │ (ap-northeast-1a)│              │ (ap-northeast-1c)│          │
│  │                 │              │                 │          │
│  │ ┌─────────────┐ │              │                 │          │
│  │ │ EC2 Instance│ │              │ (ALB用予約)     │          │
│  │ │ WealthAI    │ │              │                 │          │
│  │ │ Server      │ │              │                 │          │
│  │ └─────────────┘ │              │                 │          │
│  └─────────────────┘              └─────────────────┘          │
│           │                                                    │
│           ▼                                                    │
│  ┌─────────────────┐                                          │
│  │ Internet Gateway│                                          │
│  └─────────────────┘                                          │
└─────────────────────────────────────────────────────────────────┘
```

## 🔒 セキュリティ構成

```
┌─────────────────────────────────────────────────────────────────┐
│                    Security Groups                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────┐              ┌─────────────────┐            │
│ │ ALB-SG          │              │ EC2-SG          │            │
│ │ sg-09c3675...   │              │ sg-02a78051...  │            │
│ │                 │              │                 │            │
│ │ Inbound:        │              │ Inbound:        │            │
│ │ ├─ HTTP (80)    │──────────────┤ ├─ HTTP (80)    │            │
│ │ │  0.0.0.0/0    │              │ │  0.0.0.0/0    │            │
│ │ └─ HTTPS (443)  │              │ ├─ SSH (22)     │            │
│ │    0.0.0.0/0    │              │ │  0.0.0.0/0    │            │
│ └─────────────────┘              │ └─ App (8000)   │            │
│                                  │    ALB-SG only  │            │
│                                  └─────────────────┘            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      IAM Roles                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ takehig-DefaultEC2Role                                      │ │
│ │                                                             │ │
│ │ Attached Policies:                                          │ │
│ │ ├─ WealthAI-S3-Deployment-Policy                           │ │
│ │ │  └─ s3:GetObject, s3:ListBucket                          │ │
│ │ │     (wealthai-deployments-20250731)                      │ │
│ │ └─ Other default policies...                                │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🔄 デプロイメントフロー

```
┌─────────────────────────────────────────────────────────────────┐
│                    Deployment Methods                          │
└─────────────────────────────────────────────────────────────────┘

Method 1: S3経由デプロイ (推奨)
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. Build    │───▶│ 2. Upload   │───▶│ 3. Download │───▶│ 4. Deploy   │
│ Artifact    │    │ to S3       │    │ from S3     │    │ & Restart   │
│             │    │             │    │             │    │             │
│ ├─ src/     │    │ ├─ Versioned │    │ ├─ EC2 IAM  │    │ ├─ Backup   │
│ ├─ templates│    │ ├─ Encrypted │    │ ├─ Download │    │ ├─ Deploy   │
│ ├─ metadata │    │ └─ Logged   │    │ └─ Extract  │    │ ├─ Restart  │
│ └─ deploy.sh│    │             │    │             │    │ └─ Health   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘

Method 2: 直接デプロイ
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 1. SCP      │───▶│ 2. SSH      │───▶│ 3. Restart  │
│ Transfer    │    │ Connect     │    │ Service     │
│             │    │             │    │             │
│ ├─ src/     │    │ ├─ systemctl│    │ ├─ Health   │
│ └─ templates│    │ └─ restart  │    │ └─ Check    │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 📊 データフロー

```
┌─────────────────────────────────────────────────────────────────┐
│                      Data Architecture                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ CSV Files   │───▶│ PostgreSQL  │───▶│ SQLAlchemy  │───▶│ FastAPI     │
│             │    │ Database    │    │ ORM         │    │ Endpoints   │
│ ├─ customers│    │             │    │             │    │             │
│ ├─ products │    │ ├─ 10 Tables│    │ ├─ Models   │    │ ├─ /        │
│ ├─ holdings │    │ ├─ 68 Records│    │ ├─ Sessions │    │ ├─ /customers│
│ ├─ sales_notes│   │ ├─ Indexes  │    │ └─ Queries  │    │ ├─ /products│
│ ├─ cash_inflows│  │ └─ Relations│    │             │    │ └─ 8 screens│
│ └─ events   │    │             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                            │                                    │
                            ▼                                    ▼
                   ┌─────────────┐                      ┌─────────────┐
                   │ Backup &    │                      │ Jinja2      │
                   │ Recovery    │                      │ Templates   │
                   │             │                      │             │
                   │ ├─ pg_dump  │                      │ ├─ HTML     │
                   │ └─ Restore  │                      │ ├─ Bootstrap│
                   └─────────────┘                      │ └─ FontAwesome│
                                                        └─────────────┘
```

## 🖥️ アプリケーション構成

```
┌─────────────────────────────────────────────────────────────────┐
│                    Application Stack                           │
└─────────────────────────────────────────────────────────────────┘

Web Browser
    │ HTTP/HTTPS
    ▼
┌─────────────────┐
│ Nginx           │ ← Reverse Proxy, Static Files, SSL Termination
│ Port 80/443     │
└─────────────────┘
    │ proxy_pass
    ▼
┌─────────────────┐
│ FastAPI         │ ← Python Web Framework
│ uvicorn         │
│ Port 8000       │ ← 2 Workers (systemd managed)
└─────────────────┘
    │ SQLAlchemy
    ▼
┌─────────────────┐
│ PostgreSQL 14   │ ← Database Server
│ Port 5432       │ ← Local connection only
│ wealthai DB     │
└─────────────────┘

Service Management:
┌─────────────────┐
│ systemd         │ ← Service orchestration
│ wealthai.service│
└─────────────────┘
```

## 📱 画面構成

```
┌─────────────────────────────────────────────────────────────────┐
│                      UI Architecture                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ 1. Dashboard    │    │ 2. Customers    │    │ 3. Customer     │
│ /               │    │ /customers      │    │ /customers/{id} │
│                 │    │                 │    │                 │
│ ├─ Statistics   │    │ ├─ 10 Customers │    │ ├─ Profile      │
│ ├─ Assets       │    │ ├─ Risk Level   │    │ ├─ Holdings     │
│ └─ Scenarios    │    │ └─ Net Worth    │    │ ├─ Sales Notes  │
└─────────────────┘    └─────────────────┘    │ └─ Cash Inflows │
                                              └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ 4. Products     │    │ 5. Holdings     │    │ 6. Sales Notes  │
│ /products       │    │ /holdings       │    │ /sales-notes    │
│                 │    │                 │    │                 │
│ ├─ 10 Products  │    │ ├─ 18 Holdings  │    │ ├─ 10 Notes     │
│ ├─ Bonds/Stocks │    │ ├─ P&L          │    │ ├─ Cash Inflow  │
│ └─ Risk Levels  │    │ └─ Maturity     │    │ └─ Priorities   │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐
│ 7. Cash Inflows │    │ 8. Economic     │
│ /cash-inflows   │    │ /economic-events│
│                 │    │                 │
│ ├─ 10 Predictions│    │ ├─ 5 Events     │
│ ├─ Confidence   │    │ ├─ Political    │
│ └─ Amounts      │    │ └─ Impact Level │
└─────────────────┘    └─────────────────┘
```

## 💰 コスト構成

```
┌─────────────────────────────────────────────────────────────────┐
│                    Monthly Cost Breakdown                      │
└─────────────────────────────────────────────────────────────────┘

AWS Resources:
┌─────────────────┐ $30.00  ┌─────────────────┐ $3.60
│ EC2 t3.medium   │────────▶│ Elastic IP      │
│ 24/7 Running    │         │ Static Address  │
└─────────────────┘         └─────────────────┘
         │                           │
         ▼                           ▼
┌─────────────────┐ $1.00   ┌─────────────────┐ $0.10
│ EBS Storage     │────────▶│ S3 Storage      │
│ 8GB gp3         │         │ Deployments     │
└─────────────────┘         └─────────────────┘
         │                           │
         ▼                           ▼
┌─────────────────┐ $5.00   ┌─────────────────┐
│ Data Transfer   │────────▶│ Total: ~$40/月  │
│ Outbound        │         │                 │
└─────────────────┘         └─────────────────┘
```

## 🎯 今後の拡張予定

```
┌─────────────────────────────────────────────────────────────────┐
│                    Future Architecture                         │
└─────────────────────────────────────────────────────────────────┘

Phase 1: 現在 ✅
├─ Single EC2 Instance
├─ PostgreSQL Local
├─ S3 Deployment
└─ Basic Security

Phase 2: スケーリング
├─ Application Load Balancer
├─ Multi-AZ Deployment
├─ RDS PostgreSQL
└─ Auto Scaling

Phase 3: 高可用性
├─ CloudFront CDN
├─ Route 53 DNS
├─ SSL Certificate
└─ Backup Strategy

Phase 4: 監視・運用
├─ CloudWatch Monitoring
├─ Log Aggregation
├─ Alerting
└─ Performance Optimization
```

この構成図で、WealthAI システムの全体像が把握できます！
