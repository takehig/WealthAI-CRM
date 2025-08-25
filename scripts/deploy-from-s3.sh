#!/bin/bash

# S3経由デプロイスクリプト
# Usage: ./scripts/deploy-from-s3.sh [version] [--upload-only] [--deploy-only]

set -e

# 設定
S3_BUCKET="wealthai-deployments-20250731"
EC2_HOST="57.183.66.123"
EC2_USER="ubuntu"
KEY_PATH="~/.ssh/wealthai-keypair.pem"
VERSION=${1:-$(date +%Y%m%d-%H%M%S)}
ARTIFACT_NAME="wealthai-${VERSION}.zip"

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

# アーティファクト作成
build_artifact() {
    log_info "Building artifact version: $VERSION"
    ./scripts/build-artifact.sh "$VERSION"
}

# S3アップロード
upload_to_s3() {
    log_info "Uploading $ARTIFACT_NAME to S3..."
    
    if [ ! -f "$ARTIFACT_NAME" ]; then
        log_error "Artifact $ARTIFACT_NAME not found!"
        exit 1
    fi
    
    aws s3 cp "$ARTIFACT_NAME" "s3://$S3_BUCKET/releases/" --region ap-northeast-1
    
    # メタデータも保存
    aws s3 cp "$ARTIFACT_NAME" "s3://$S3_BUCKET/latest/wealthai-latest.zip" --region ap-northeast-1
    
    log_success "Uploaded to S3: s3://$S3_BUCKET/releases/$ARTIFACT_NAME"
}

# EC2デプロイ
deploy_to_ec2() {
    log_info "Deploying version $VERSION to EC2..."
    
    # EC2でS3からダウンロード&デプロイ
    ssh -i $KEY_PATH $EC2_USER@$EC2_HOST "
        set -e
        cd /tmp
        
        echo '🌐 Downloading from S3...'
        aws s3 cp s3://$S3_BUCKET/releases/$ARTIFACT_NAME . --region ap-northeast-1
        
        echo '📦 Extracting artifact...'
        rm -rf wealthai-deploy
        unzip -q $ARTIFACT_NAME
        cd wealthai
        
        echo '🚀 Running deployment...'
        chmod +x deploy.sh
        ./deploy.sh
        
        echo '🧹 Cleaning up...'
        cd /tmp
        rm -rf wealthai-deploy $ARTIFACT_NAME
    "
    
    log_success "Deployment completed!"
}

# ヘルスチェック
health_check() {
    log_info "Performing health check..."
    sleep 5
    
    if curl -s "http://$EC2_HOST/" | grep -q "WealthAI"; then
        log_success "✅ Health check passed!"
        return 0
    else
        log_error "❌ Health check failed!"
        return 1
    fi
}

# S3のリリース一覧表示
list_releases() {
    log_info "Available releases in S3:"
    aws s3 ls "s3://$S3_BUCKET/releases/" --region ap-northeast-1 | grep "wealthai-" | sort -r
}

# ロールバック
rollback() {
    local rollback_version=$1
    if [ -z "$rollback_version" ]; then
        log_error "Rollback version not specified!"
        list_releases
        exit 1
    fi
    
    log_warning "Rolling back to version: $rollback_version"
    VERSION="$rollback_version"
    ARTIFACT_NAME="wealthai-${VERSION}.zip"
    deploy_to_ec2
}

# メイン処理
main() {
    case "${1:-}" in
        --upload-only)
            build_artifact
            upload_to_s3
            ;;
        --deploy-only)
            deploy_to_ec2
            health_check
            ;;
        --list)
            list_releases
            ;;
        --rollback)
            rollback "$2"
            ;;
        --help)
            echo "Usage: $0 [version] [options]"
            echo "Options:"
            echo "  --upload-only  : Build and upload artifact only"
            echo "  --deploy-only  : Deploy existing artifact only"
            echo "  --list         : List available releases"
            echo "  --rollback VER : Rollback to specified version"
            echo "  --help         : Show this help"
            ;;
        "")
            # フルデプロイ
            build_artifact
            upload_to_s3
            deploy_to_ec2
            health_check
            ;;
        *)
            # バージョン指定
            VERSION="$1"
            ARTIFACT_NAME="wealthai-${VERSION}.zip"
            shift
            main "$@"
            ;;
    esac
}

# 実行
main "$@"
