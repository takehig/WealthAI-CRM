#!/bin/bash

# WealthAI デプロイスクリプト
# Usage: ./scripts/deploy.sh [--setup] [--restart-only]

set -e

# 設定
EC2_HOST="57.183.66.123"
EC2_USER="ubuntu"
KEY_PATH="~/.ssh/wealthai-keypair.pem"
APP_DIR="/home/ubuntu/wealthai"
SERVICE_NAME="wealthai"

# 色付きログ
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 初期セットアップ
setup_environment() {
    log_info "Setting up production environment..."
    
    # systemdサービスファイルを転送・設定
    log_info "Setting up systemd service..."
    scp -i $KEY_PATH config/wealthai.service $EC2_USER@$EC2_HOST:/tmp/
    ssh -i $KEY_PATH $EC2_USER@$EC2_HOST "
        sudo mv /tmp/wealthai.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable $SERVICE_NAME
    "
    
    # Nginx設定
    log_info "Setting up Nginx configuration..."
    scp -i $KEY_PATH config/nginx-wealthai.conf $EC2_USER@$EC2_HOST:/tmp/
    ssh -i $KEY_PATH $EC2_USER@$EC2_HOST "
        sudo mv /tmp/nginx-wealthai.conf /etc/nginx/sites-available/wealthai
        sudo ln -sf /etc/nginx/sites-available/wealthai /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/default
        sudo nginx -t && sudo systemctl reload nginx
    "
    
    # 現在のプロセスを停止
    log_info "Stopping current application process..."
    ssh -i $KEY_PATH $EC2_USER@$EC2_HOST "pkill -f 'python.*uvicorn' || true"
    
    log_success "Environment setup completed!"
}

# アプリケーションデプロイ
deploy_application() {
    log_info "Deploying application to AWS..."
    
    # ファイル転送
    log_info "Transferring application files..."
    scp -i $KEY_PATH -r src/ templates/ requirements.txt .env $EC2_USER@$EC2_HOST:$APP_DIR/
    
    # 依存関係更新
    log_info "Updating dependencies..."
    ssh -i $KEY_PATH $EC2_USER@$EC2_HOST "
        cd $APP_DIR
        source venv/bin/activate
        pip install -r requirements.txt --quiet
    "
    
    # サービス再起動
    restart_service
    
    log_success "Application deployed successfully!"
}

# サービス再起動
restart_service() {
    log_info "Restarting WealthAI service..."
    ssh -i $KEY_PATH $EC2_USER@$EC2_HOST "
        sudo systemctl restart $SERVICE_NAME
        sleep 3
        sudo systemctl status $SERVICE_NAME --no-pager
    "
    
    # ヘルスチェック
    log_info "Performing health check..."
    sleep 5
    if curl -s http://$EC2_HOST/ | grep -q "WealthAI CRM"; then
        log_success "Health check passed! Application is running."
    else
        log_error "Health check failed! Please check the logs."
        exit 1
    fi
}

# ログ表示
show_logs() {
    log_info "Showing recent application logs..."
    ssh -i $KEY_PATH $EC2_USER@$EC2_HOST "
        sudo journalctl -u $SERVICE_NAME -n 20 --no-pager
    "
}

# ステータス確認
check_status() {
    log_info "Checking application status..."
    ssh -i $KEY_PATH $EC2_USER@$EC2_HOST "
        echo '=== Service Status ==='
        sudo systemctl status $SERVICE_NAME --no-pager
        echo
        echo '=== Port Status ==='
        ss -tlnp | grep 8000 || echo 'Port 8000 not listening'
        echo
        echo '=== Recent Logs ==='
        sudo journalctl -u $SERVICE_NAME -n 5 --no-pager
    "
}

# メイン処理
main() {
    case "${1:-}" in
        --setup)
            setup_environment
            deploy_application
            ;;
        --restart-only)
            restart_service
            ;;
        --logs)
            show_logs
            ;;
        --status)
            check_status
            ;;
        --help)
            echo "Usage: $0 [--setup|--restart-only|--logs|--status|--help]"
            echo "  --setup       : Initial environment setup + deploy"
            echo "  --restart-only: Restart service only"
            echo "  --logs        : Show recent logs"
            echo "  --status      : Check application status"
            echo "  (no args)     : Deploy application"
            ;;
        "")
            deploy_application
            ;;
        *)
            log_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
}

# スクリプト実行
main "$@"
