#!/bin/bash

# WealthAI 統合デプロイスクリプト
# Usage: ./scripts/deploy-unified.sh [--s3|--direct] [options]

set -e

# 設定
DEPLOY_METHOD=${1:-"--s3"}  # デフォルトはS3経由

# 色付きログ
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# S3経由デプロイ
deploy_via_s3() {
    log_info "Using S3-based deployment method"
    shift  # --s3 を除去
    ./scripts/deploy-from-s3.sh "$@"
}

# 直接デプロイ（従来のscp方式）
deploy_direct() {
    log_info "Using direct deployment method (scp + systemd)"
    
    EC2_HOST="57.183.66.123"
    EC2_USER="ubuntu"
    KEY_PATH="~/.ssh/wealthai-keypair.pem"
    
    # ファイル転送
    log_info "Transferring files to EC2..."
    scp -i $KEY_PATH -r src/ templates/ $EC2_USER@$EC2_HOST:~/wealthai/
    
    # サービス再起動
    log_info "Restarting application service..."
    ssh -i $KEY_PATH $EC2_USER@$EC2_HOST "sudo systemctl restart wealthai"
    
    # ヘルスチェック
    log_info "Performing health check..."
    sleep 5
    if curl -s http://$EC2_HOST/ | grep -q "WealthAI"; then
        log_success "✅ Direct deployment successful!"
    else
        log_error "❌ Direct deployment failed!"
        exit 1
    fi
}

# ヘルプ表示
show_help() {
    echo "WealthAI Deployment Script"
    echo ""
    echo "Usage: $0 [method] [options]"
    echo ""
    echo "Methods:"
    echo "  --s3      : S3-based deployment (recommended, default)"
    echo "  --direct  : Direct deployment via scp"
    echo ""
    echo "S3 Options (when using --s3):"
    echo "  [version]     : Specify version (default: timestamp)"
    echo "  --upload-only : Build and upload artifact only"
    echo "  --deploy-only : Deploy existing artifact only"
    echo "  --list        : List available releases"
    echo "  --rollback VER: Rollback to specified version"
    echo ""
    echo "Examples:"
    echo "  $0                    # S3 deployment with auto version"
    echo "  $0 --s3 v1.2.3       # S3 deployment with specific version"
    echo "  $0 --s3 --list       # List S3 releases"
    echo "  $0 --direct          # Direct deployment"
    echo ""
}

# メイン処理
main() {
    case "${1:-}" in
        --s3)
            deploy_via_s3 "$@"
            ;;
        --direct)
            deploy_direct
            ;;
        --help|-h)
            show_help
            ;;
        "")
            # デフォルトはS3経由
            deploy_via_s3
            ;;
        *)
            # 引数がある場合はS3経由として処理
            deploy_via_s3 --s3 "$@"
            ;;
    esac
}

# 実行
main "$@"
