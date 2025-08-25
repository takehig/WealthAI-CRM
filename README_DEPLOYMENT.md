# WealthAI デプロイメントガイド

## 🚀 AWS環境での改修・反映方法

### 現在の環境
- **本番URL**: http://57.183.66.123/
- **EC2インスタンス**: i-08b1d37a074cfe046 (t3.medium)
- **サービス管理**: systemd (wealthai.service)
- **Webサーバー**: Nginx (リバースプロキシ)

## 📋 デプロイ方法

### Method 1: 推奨デプロイ（systemd使用）
```bash
# 1. ファイルを転送
scp -i ~/.ssh/wealthai-keypair.pem -r src/ templates/ ubuntu@57.183.66.123:~/wealthai/

# 2. サービス再起動
ssh -i ~/.ssh/wealthai-keypair.pem ubuntu@57.183.66.123 "sudo systemctl restart wealthai"

# 3. 動作確認
curl http://57.183.66.123/
```

### Method 2: 自動デプロイスクリプト
```bash
# 完全デプロイ
./scripts/deploy.sh

# サービス再起動のみ
./scripts/deploy.sh --restart-only

# ログ確認
./scripts/deploy.sh --logs

# ステータス確認
./scripts/deploy.sh --status
```

### Method 3: 開発用クイックデプロイ
```bash
./scripts/quick-deploy.sh
```

## 🔧 運用コマンド

### サービス管理
```bash
# サービス状態確認
ssh -i ~/.ssh/wealthai-keypair.pem ubuntu@57.183.66.123 "sudo systemctl status wealthai"

# サービス再起動
ssh -i ~/.ssh/wealthai-keypair.pem ubuntu@57.183.66.123 "sudo systemctl restart wealthai"

# ログ確認
ssh -i ~/.ssh/wealthai-keypair.pem ubuntu@57.183.66.123 "sudo journalctl -u wealthai -f"
```

### データベース操作
```bash
# データベース接続
ssh -i ~/.ssh/wealthai-keypair.pem ubuntu@57.183.66.123 "PGPASSWORD=wealthai123 psql -h localhost -U wealthai_user -d wealthai"

# データ再インポート
ssh -i ~/.ssh/wealthai-keypair.pem ubuntu@57.183.66.123 "cd ~/wealthai && source venv/bin/activate && python src/utils/import_data.py"
```

## 📁 ファイル構成

### 重要なファイル
- `/etc/systemd/system/wealthai.service` - systemdサービス設定
- `/etc/nginx/sites-available/wealthai` - Nginx設定
- `/home/ubuntu/wealthai/` - アプリケーションディレクトリ

### ログファイル
- `sudo journalctl -u wealthai` - アプリケーションログ
- `/var/log/nginx/wealthai_access.log` - Nginxアクセスログ
- `/var/log/nginx/wealthai_error.log` - Nginxエラーログ

## 🚨 トラブルシューティング

### アプリケーションが起動しない
```bash
# サービス状態確認
sudo systemctl status wealthai

# ログ確認
sudo journalctl -u wealthai -n 20

# 手動起動テスト
cd /home/ubuntu/wealthai
source venv/bin/activate
python -c "import sys; sys.path.append('src'); from main import app; print('Import OK')"
```

### データベース接続エラー
```bash
# PostgreSQL状態確認
sudo systemctl status postgresql

# 接続テスト
PGPASSWORD=wealthai123 psql -h localhost -U wealthai_user -d wealthai -c "SELECT 1;"
```

### Nginx設定エラー
```bash
# 設定テスト
sudo nginx -t

# 設定リロード
sudo systemctl reload nginx
```

## 🔄 開発ワークフロー

### 1. ローカルで開発
```bash
cd /mnt/c/Users/takehig/QCHAT/.qchat_projects/WealthAI
# コードを修正
```

### 2. テスト
```bash
# ローカルでテスト
source venv/bin/activate
python src/main.py
```

### 3. デプロイ
```bash
# AWS環境に反映
scp -i ~/.ssh/wealthai-keypair.pem -r src/ templates/ ubuntu@57.183.66.123:~/wealthai/
ssh -i ~/.ssh/wealthai-keypair.pem ubuntu@57.183.66.123 "sudo systemctl restart wealthai"
```

### 4. 確認
```bash
# 動作確認
curl http://57.183.66.123/
```

## 📊 監視・メンテナンス

### 定期確認項目
- [ ] アプリケーション稼働状況
- [ ] データベース接続状況
- [ ] ディスク使用量
- [ ] メモリ使用量
- [ ] ログファイルサイズ

### 月次メンテナンス
```bash
# システムアップデート
sudo apt update && sudo apt upgrade -y

# ログローテーション確認
sudo logrotate -f /etc/logrotate.conf

# ディスク使用量確認
df -h
```

## 🎯 次のステップ

### 改善予定
1. **CI/CD パイプライン** - GitHub Actions
2. **SSL証明書** - Let's Encrypt
3. **ドメイン設定** - Route 53
4. **バックアップ** - 自動バックアップ
5. **モニタリング** - CloudWatch

これで改修・反映の仕組みが整いました！
