# WealthAI デプロイメントガイド

## 概要
ローカル環境で開発したアプリケーションをAWS環境に反映する手順

## デプロイメント方法

### Method 1: 手動デプロイ（現在の方法）
```bash
# 1. ローカルで変更を加える
# 2. ファイルをEC2に転送
scp -i ~/.ssh/wealthai-keypair.pem -r src/ ubuntu@57.183.66.123:~/wealthai/
# 3. アプリケーションを再起動
ssh -i ~/.ssh/wealthai-keypair.pem ubuntu@57.183.66.123 "sudo systemctl restart wealthai"
```

### Method 2: Git経由デプロイ（推奨）
```bash
# 1. GitHubリポジトリにpush
git add .
git commit -m "Update application"
git push origin main

# 2. EC2でpull & restart
ssh -i ~/.ssh/wealthai-keypair.pem ubuntu@57.183.66.123 "
cd ~/wealthai
git pull origin main
sudo systemctl restart wealthai
"
```

### Method 3: 自動デプロイスクリプト
```bash
# deploy.sh を実行
./scripts/deploy.sh
```

## 必要な設定

### 1. systemdサービス設定
### 2. Nginxリバースプロキシ設定
### 3. 自動デプロイスクリプト作成
### 4. ログ監視設定

## セットアップ手順
1. systemdサービス作成
2. Nginx設定
3. デプロイスクリプト作成
4. 動作確認
