# WealthAI 技術仕様書

## 📋 システム概要

### プロジェクト名
**WealthAI CRM System**
- ウェルスマネジメント向けAIエージェントのデモ用CRMシステム
- 3つのスクリーニングシナリオ対応
- AWS環境での本番稼働

### アクセス情報
- **本番URL**: http://57.183.66.123/
- **開発環境**: WSL Ubuntu 24.04
- **デプロイ方式**: S3経由 + 直接デプロイ

## 🏗️ インフラ仕様

### AWS環境
| リソース | 仕様 | 用途 |
|---------|------|------|
| **EC2** | t3.medium (2vCPU, 4GB RAM) | アプリケーションサーバー |
| **OS** | Ubuntu 22.04 LTS | ベースOS |
| **VPC** | 10.0.0.0/16 | ネットワーク分離 |
| **Subnet** | 10.0.1.0/24 (1a), 10.0.2.0/24 (1c) | 冗長性確保 |
| **Elastic IP** | 57.183.66.123 | 固定IPアドレス |
| **S3 Bucket** | wealthai-deployments-20250731 | デプロイメント用 |

### セキュリティ
| 項目 | 設定 | 説明 |
|------|------|------|
| **Security Group** | sg-02a78051524c11af9 | EC2用セキュリティグループ |
| **HTTP (80)** | 0.0.0.0/0 | Webアクセス用 |
| **SSH (22)** | 0.0.0.0/0 | 管理用（要制限推奨） |
| **App (8000)** | 内部のみ | アプリケーション直接アクセス |
| **IAM Role** | takehig-DefaultEC2Role | S3アクセス権限付与 |

## 💻 アプリケーション仕様

### 技術スタック
| レイヤー | 技術 | バージョン | 用途 |
|----------|------|------------|------|
| **Frontend** | Jinja2 + Bootstrap 5 | 3.1.6 / 5.1.3 | テンプレートエンジン + UI |
| **Backend** | FastAPI + uvicorn | 0.116.1 / 0.35.0 | Web API フレームワーク |
| **ORM** | SQLAlchemy | 2.0.42 | データベースORM |
| **Database** | PostgreSQL | 14 | メインデータベース |
| **Web Server** | Nginx | 1.18.0 | リバースプロキシ |
| **Process Manager** | systemd | - | サービス管理 |
| **Language** | Python | 3.10 | 開発言語 |

### アプリケーション構成
```
/home/ubuntu/wealthai/
├── src/                    # アプリケーションコード
│   ├── main.py            # FastAPI メインアプリ
│   ├── models/            # SQLAlchemy モデル
│   ├── routes/            # API ルート定義
│   ├── database.py        # DB接続設定
│   └── utils/             # ユーティリティ
├── templates/             # Jinja2 テンプレート
├── static/               # 静的ファイル（CSS, JS）
├── data/csv/             # サンプルデータ
├── sql/schema/           # データベーススキーマ
├── venv/                 # Python仮想環境
├── requirements.txt      # Python依存関係
└── .env                  # 環境変数
```

## 🗄️ データベース仕様

### PostgreSQL設定
| 項目 | 値 | 説明 |
|------|----|----- |
| **データベース名** | wealthai | メインDB |
| **ユーザー** | wealthai_user | アプリケーション用ユーザー |
| **パスワード** | wealthai123 | 認証用 |
| **ホスト** | localhost | ローカル接続 |
| **ポート** | 5432 | デフォルトポート |

### テーブル構成
| テーブル名 | 件数 | 説明 |
|-----------|------|------|
| **sales_representatives** | 5件 | 営業担当者マスター |
| **customers** | 10件 | 顧客マスター |
| **products** | 10件 | 商品マスター |
| **holdings** | 18件 | 保有商品データ |
| **sales_notes** | 10件 | 営業メモ |
| **cash_inflows** | 10件 | 入金予測データ |
| **economic_events** | 5件 | 経済・政治イベント |
| **market_data** | 0件 | 市場データ（空） |
| **transactions** | 0件 | 取引履歴（空） |
| **recommendations** | 0件 | 推奨履歴（空） |

## 🌐 Web画面仕様

### 実装済み画面（8画面）
| 画面名 | URL | 機能 |
|--------|-----|------|
| **ダッシュボード** | `/` | 統計概要、システム説明 |
| **顧客一覧** | `/customers` | 全顧客の一覧表示 |
| **顧客詳細** | `/customers/{id}` | 個別顧客の詳細情報 |
| **商品一覧** | `/products` | 取扱商品の一覧 |
| **保有商品一覧** | `/holdings` | 全顧客の保有商品 |
| **営業メモ一覧** | `/sales-notes` | 営業活動記録 |
| **入金予測一覧** | `/cash-inflows` | 入金予測データ |
| **経済イベント一覧** | `/economic-events` | 政治・経済イベント |

### UI特徴
- **レスポンシブデザイン**: Bootstrap 5使用
- **直感的ナビゲーション**: サイドバーメニュー
- **データ可視化**: 統計カード、バッジ、テーブル
- **リンク連携**: 顧客詳細への遷移
- **色分け表示**: リスクレベル、優先度、ステータス

## 🔄 デプロイメント仕様

### S3経由デプロイ（推奨）
```bash
# アーティファクト作成
./scripts/build-artifact.sh [version]

# S3アップロード + EC2デプロイ
./scripts/deploy-from-s3.sh [version]

# ロールバック
./scripts/deploy-from-s3.sh --rollback [version]
```

### 直接デプロイ
```bash
# ファイル転送 + サービス再起動
scp -i ~/.ssh/wealthai-keypair.pem -r src/ templates/ ubuntu@57.183.66.123:~/wealthai/
ssh -i ~/.ssh/wealthai-keypair.pem ubuntu@57.183.66.123 "sudo systemctl restart wealthai"
```

### デプロイフロー
1. **アーティファクト作成**: src/, templates/, metadata をzip化
2. **S3アップロード**: バージョニング・暗号化して保存
3. **EC2ダウンロード**: IAMロールでS3からダウンロード
4. **バックアップ作成**: 現在のアプリケーションをバックアップ
5. **デプロイ実行**: 新しいファイルを配置
6. **サービス再起動**: systemdでアプリケーション再起動
7. **ヘルスチェック**: 正常性確認、失敗時は自動ロールバック

## 🔧 運用仕様

### サービス管理
```bash
# サービス状態確認
sudo systemctl status wealthai

# サービス再起動
sudo systemctl restart wealthai

# ログ確認
sudo journalctl -u wealthai -f
```

### 監視項目
- **アプリケーション稼働状況**: systemd status
- **データベース接続**: PostgreSQL connection
- **ディスク使用量**: df -h
- **メモリ使用量**: free -h
- **ログファイルサイズ**: du -h /var/log/

### バックアップ
- **アプリケーション**: デプロイ時に自動バックアップ
- **データベース**: pg_dump による手動バックアップ
- **設定ファイル**: Git管理

## 📊 パフォーマンス仕様

### 現在の性能
- **レスポンス時間**: 平均 < 100ms
- **同時接続数**: 未測定（小規模想定）
- **データ処理**: 68件のサンプルデータで十分な性能

### スケーラビリティ
- **垂直スケーリング**: EC2インスタンスタイプ変更
- **水平スケーリング**: ALB + 複数EC2（将来対応）
- **データベース**: RDS移行（将来対応）

## 💰 コスト仕様

### 月額運用コスト
| 項目 | 金額 | 説明 |
|------|------|------|
| **EC2 t3.medium** | ~$30 | 24/7稼働 |
| **Elastic IP** | ~$3.6 | 固定IP |
| **EBS 8GB** | ~$1 | ストレージ |
| **S3ストレージ** | ~$0.1 | デプロイメント用 |
| **データ転送** | ~$5 | アウトバウンド |
| **合計** | **~$40** | 月額総コスト |

## 🎯 将来拡張仕様

### Phase 2: スケーリング
- Application Load Balancer追加
- Multi-AZ配置
- RDS PostgreSQL移行
- Auto Scaling設定

### Phase 3: 高可用性
- CloudFront CDN
- Route 53 DNS
- SSL証明書（Let's Encrypt）
- 自動バックアップ

### Phase 4: 監視・運用
- CloudWatch監視
- ログ集約
- アラート設定
- パフォーマンス最適化

この技術仕様書により、システムの詳細な構成と運用方法が明確になります。
