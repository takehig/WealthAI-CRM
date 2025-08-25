# WealthAI CRM System

ウェルスマネジメント向けCRMデータ参照システム

## 機能

- 顧客管理
- 商品管理
- 保有資産管理
- 営業メモ管理
- 入金予測管理
- Amazon Bedrock Claude 3チャット機能
- 債券保有顧客分析

## 技術スタック

- **Backend**: FastAPI + SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: Jinja2 Templates + Bootstrap
- **AI**: Amazon Bedrock Claude 3
- **Deployment**: GitHub + SSH

## セットアップ

```bash
# 依存関係インストール
pip install -r requirements.txt

# データベース設定
# .env ファイルを作成（.env.example を参考）

# アプリケーション起動
python src/main.py
```

## API エンドポイント

- `GET /` - ダッシュボード
- `GET /customers` - 顧客一覧
- `GET /customers/{id}` - 顧客詳細
- `POST /api/chat` - Bedrockチャット
- `GET /api/customers/bond-holders` - 債券保有顧客

## デプロイ

```bash
# ローカル開発後
git add .
git commit -m "機能追加"
git push origin main

# EC2で更新
./deploy/update.sh
```
