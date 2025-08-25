#!/bin/bash

# WealthAI クイックデプロイスクリプト
# 開発中の素早い反映用

set -e

EC2_HOST="57.183.66.123"
EC2_USER="ubuntu"
KEY_PATH="~/.ssh/wealthai-keypair.pem"

echo "🚀 Quick deploying to AWS..."

# ソースコードのみ転送
echo "📁 Transferring source files..."
scp -i $KEY_PATH -r src/ templates/ $EC2_USER@$EC2_HOST:~/wealthai/

# アプリケーション再起動
echo "🔄 Restarting application..."
ssh -i $KEY_PATH $EC2_USER@$EC2_HOST "
    cd ~/wealthai
    pkill -f 'python.*uvicorn' || true
    sleep 2
    source venv/bin/activate
    nohup python -c \"
import uvicorn
import sys
sys.path.append('src')
from main import app
uvicorn.run(app, host='0.0.0.0', port=8000)
\" > app.log 2>&1 &
"

# ヘルスチェック
echo "🏥 Health check..."
sleep 5
if curl -s http://$EC2_HOST:8000/ | grep -q "WealthAI CRM"; then
    echo "✅ Deployment successful! http://$EC2_HOST:8000/"
else
    echo "❌ Deployment failed!"
    exit 1
fi
