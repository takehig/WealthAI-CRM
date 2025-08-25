#!/bin/bash

# WealthAI アーティファクト作成スクリプト
# Usage: ./scripts/build-artifact.sh [version]

set -e

# 設定
PROJECT_DIR="/mnt/c/Users/takehig/QCHAT/.qchat_projects/WealthAI"
BUILD_DIR="$PROJECT_DIR/build"
VERSION=${1:-$(date +%Y%m%d-%H%M%S)}
ARTIFACT_NAME="wealthai-${VERSION}.zip"

# 色付きログ
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# ビルドディレクトリ準備
log_info "Preparing build directory..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/wealthai"

# 必要なファイルをコピー
log_info "Copying application files..."
cp -r src/ "$BUILD_DIR/wealthai/"
cp -r templates/ "$BUILD_DIR/wealthai/"
cp requirements.txt "$BUILD_DIR/wealthai/"
cp .env "$BUILD_DIR/wealthai/"

# データファイルをコピー（オプション）
if [ -d "data/csv" ]; then
    log_info "Copying data files..."
    cp -r data/ "$BUILD_DIR/wealthai/"
fi

# SQLファイルをコピー（オプション）
if [ -d "sql" ]; then
    log_info "Copying SQL files..."
    cp -r sql/ "$BUILD_DIR/wealthai/"
fi

# デプロイメント情報を追加
log_info "Adding deployment metadata..."
cat > "$BUILD_DIR/wealthai/deployment-info.json" << EOF
{
    "version": "$VERSION",
    "build_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "build_host": "$(hostname)",
    "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "git_branch": "$(git branch --show-current 2>/dev/null || echo 'unknown')"
}
EOF

# EC2用デプロイスクリプトを追加
log_info "Adding deployment script..."
cat > "$BUILD_DIR/wealthai/deploy.sh" << 'EOF'
#!/bin/bash
# EC2上で実行されるデプロイスクリプト

set -e

APP_DIR="/home/ubuntu/wealthai"
BACKUP_DIR="/home/ubuntu/wealthai-backup-$(date +%Y%m%d-%H%M%S)"

echo "🚀 Starting deployment..."

# バックアップ作成
if [ -d "$APP_DIR" ]; then
    echo "📦 Creating backup..."
    cp -r "$APP_DIR" "$BACKUP_DIR"
fi

# アプリケーション停止
echo "⏹️  Stopping application..."
sudo systemctl stop wealthai || true

# 新しいファイルを配置
echo "📁 Deploying new files..."
mkdir -p "$APP_DIR"
cp -r * "$APP_DIR/"

# 権限設定
chown -R ubuntu:ubuntu "$APP_DIR"

# 依存関係更新
echo "📦 Updating dependencies..."
cd "$APP_DIR"
source venv/bin/activate
pip install -r requirements.txt --quiet

# アプリケーション開始
echo "▶️  Starting application..."
sudo systemctl start wealthai

# ヘルスチェック
echo "🏥 Health check..."
sleep 5
if curl -s http://localhost/ | grep -q "WealthAI"; then
    echo "✅ Deployment successful!"
    # バックアップ削除（成功時）
    rm -rf "$BACKUP_DIR"
else
    echo "❌ Deployment failed! Rolling back..."
    sudo systemctl stop wealthai
    rm -rf "$APP_DIR"
    mv "$BACKUP_DIR" "$APP_DIR"
    sudo systemctl start wealthai
    exit 1
fi
EOF

chmod +x "$BUILD_DIR/wealthai/deploy.sh"

# アーティファクト作成
log_info "Creating artifact: $ARTIFACT_NAME"
cd "$BUILD_DIR"
zip -r "$PROJECT_DIR/$ARTIFACT_NAME" wealthai/ > /dev/null

# 結果表示
log_success "Artifact created successfully!"
echo "📦 Artifact: $PROJECT_DIR/$ARTIFACT_NAME"
echo "🏷️  Version: $VERSION"
echo "📊 Size: $(du -h "$PROJECT_DIR/$ARTIFACT_NAME" | cut -f1)"

# メタデータ表示
if command -v jq &> /dev/null; then
    echo "ℹ️  Metadata:"
    cat "$BUILD_DIR/wealthai/deployment-info.json" | jq .
fi

# クリーンアップ
rm -rf "$BUILD_DIR"

echo ""
echo "Next steps:"
echo "1. Upload to S3: aws s3 cp $ARTIFACT_NAME s3://wealthai-deployments-20250731/releases/"
echo "2. Deploy on EC2: ./scripts/deploy-from-s3.sh $VERSION"
