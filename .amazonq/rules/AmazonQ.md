# Amazon Q Developer Context

## Project Overview
**WealthAI Enterprise Systems** - 金融商品管理とAI対話機能を統合したエンタープライズシステム

## 📚 GitHub使用ルール（必須）

### 基本原則
- **すべての変更はGitHubで管理する**
- **作業前に必ずpullして最新状態にする**
- **作業後は必ずcommit & pushする**

### リポジトリ構成
```
WealthAI Enterprise Systems
├── WealthAI-CRM (https://github.com/takehig/WealthAI-CRM)
├── AIChat-System (https://github.com/takehig/AIChat-System)
├── ProductMaster-System (https://github.com/takehig/ProductMaster-System)
├── ProductMaster-MCP (https://github.com/takehig/ProductMaster-MCP)
└── enterprise-systemd (https://github.com/takehig/enterprise-systemd)
```

### コミットメッセージ形式
```
[種別] 概要説明

[ADD] 新機能追加
[FIX] バグ修正
[UPDATE] 既存機能改善
[DOC] ドキュメント更新
[CONFIG] 設定変更
[REFACTOR] リファクタリング

例:
[ADD] ProductMaster MCP拡張アーキテクチャ実装
[FIX] JavaScript APIパス問題修正
```

### 作業フロー
```bash
# 1. 作業開始時
git pull origin main

# 2. 作業中
git add .
git commit -m "[ADD] MarketData MCP基本実装"

# 3. 作業完了時
git push origin main
```

## Architecture

### Multi-Service Architecture
```
Nginx Proxy (Port 80)
├── Portal (/) → Static HTML
├── CRM (/crm/) → Port 8000
├── ProductMaster (/products/) → Port 8001
└── AIChat (/aichat/) → Port 8002
    └── ProductMaster MCP → Port 8003
```

### Technology Stack
- **Backend**: Python FastAPI, asyncio
- **Frontend**: HTML5, JavaScript ES6+, Bootstrap 5
- **Database**: PostgreSQL
- **AI**: Amazon Bedrock Claude 3 Sonnet
- **Protocol**: Model Context Protocol (MCP)
- **Infrastructure**: AWS EC2, Nginx, systemd
- **Version Control**: GitHub（必須）

## Key Components

### 1. CRM System (`./CRM/`)
- **Purpose**: 顧客管理、Bedrock チャット機能
- **Repository**: https://github.com/takehig/WealthAI-CRM
- **Main Files**: `src/main.py`, `templates/`
- **Features**: Customer management, Bedrock integration

### 2. ProductMaster System (`./ProductMaster/`)
- **Purpose**: 商品情報管理、CSV処理
- **Repository**: https://github.com/takehig/ProductMaster-System
- **Main Files**: `src/main.py`, `templates/`
- **Features**: Product CRUD, CSV import/export, encoding support

### 3. AIChat System (`./AIChat/`)
- **Purpose**: AI対話、MCP統合
- **Repository**: https://github.com/takehig/AIChat-System
- **Main Files**: `backend/main.py`, `backend/mcp_manager.py`, `web/index.html`
- **Features**: AI chat, MCP integration, extensible architecture

### 4. ProductMaster MCP (`./ProductMaster-MCP/`)
- **Purpose**: 商品検索MCP サーバー
- **Repository**: https://github.com/takehig/ProductMaster-MCP
- **Main Files**: `simple_http_mcp_8003.py`
- **Features**: Product search API, MCP protocol compliance

## Development Patterns

### MCP Extension Pattern
```python
# In mcp_manager.py
'new_mcp': {
    'name': 'NewMCP',
    'description': '新しいMCP機能',
    'url': 'http://localhost:8004',
    'enabled': False
}
```

### API Response Pattern
```python
# Standard API response
{
    "status": "success|error",
    "data": {...},
    "message": "説明メッセージ",
    "timestamp": "2025-08-30T03:00:00Z"
}
```

### Error Handling Pattern
```python
try:
    # Process logic
    result = await process_function()
    return {"status": "success", "data": result}
except Exception as e:
    logger.error(f"Error: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

## Common Tasks

### Adding New MCP
1. Create MCP server on new port
2. Update `mcp_manager.py` configuration
3. Add systemd service
4. Update frontend if needed
5. **GitHub**: Commit & push changes

### Service Management
```bash
# Start all services
./enterprise-systemd/scripts/manage-services.sh start

# Check MCP health
./enterprise-systemd/scripts/mcp-check-wsl.sh
```

### Git Workflow
```bash
# Before starting work
git pull origin main

# During development
git add .
git commit -m "[ADD] 新機能実装"

# After completion
git push origin main
```

## Code Quality Rules

### Python
- **PEP 8準拠**: コードスタイル統一
- **日本語コメント**: 理解しやすさ重視
- **try-catch必須**: エラーハンドリング徹底

### JavaScript
- **ES6+使用**: モダンな記法
- **[MCP DEBUG]プレフィックス**: デバッグログ統一
- **絶対パス使用**: プロキシ環境対応

### HTML
- **HTML5準拠**: 標準準拠
- **Bootstrap 5**: UI統一
- **レスポンシブ対応**: モバイル対応

## Important Configurations

### Nginx Proxy Rules
```nginx
location /crm/ { proxy_pass http://127.0.0.1:8000/; }
location /products/ { proxy_pass http://127.0.0.1:8001/; }
location /aichat/ { proxy_pass http://127.0.0.1:8002/; }
```

### JavaScript API Paths
```javascript
// Use absolute paths for proxy compatibility
fetch('/aichat/api/status')
fetch('/aichat/api/mcp/toggle')
```

### Database Schema
```sql
-- products table
CREATE TABLE products (
    product_code VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    product_type VARCHAR(100),
    currency VARCHAR(10),
    description TEXT,
    -- ... other fields
);
```

## Security Considerations
- No hardcoded credentials in code
- Use environment variables for sensitive data
- IAM role: `takehig-DefaultEC2Role`
- Bedrock model: `anthropic.claude-3-sonnet-20240229-v1:0`
- **GitHub**: 機密情報は .gitignore で除外

## Performance Notes
- Async/await pattern for I/O operations
- Connection pooling for database
- Nginx proxy for load distribution
- systemd for process management

## Troubleshooting Guide

### MCP Issues
- **Symptom**: "MCP: 読み込み中..." stuck
- **Cause**: JavaScript API path issues
- **Solution**: Use absolute paths `/aichat/api/status`

### Encoding Issues
- **Symptom**: CSV文字化け
- **Cause**: Character encoding mismatch
- **Solution**: Use UTF-8 BOM for Excel compatibility

### Service Startup Issues
- **Symptom**: Service fails to start
- **Cause**: Python syntax errors, port conflicts
- **Solution**: Check logs, verify syntax, check port usage

### Git Issues
- **Symptom**: Push rejected
- **Cause**: Local branch behind remote
- **Solution**: `git pull origin main` then push

## 🔧 AWS SSM実行ルール

### SSM経由でのEC2操作
- **SSM実行ユーザー**: `root`として実行される
- **アプリケーション所有者**: `ec2-user`
- **Git操作時の注意**: 必ず`sudo -u ec2-user`を使用

### 正しいSSMコマンド例
```bash
# ❌ 間違い（権限エラー）
cd /home/ec2-user/AIChat && git pull origin main

# ✅ 正しい
sudo -u ec2-user bash -c 'cd /home/ec2-user/AIChat && git pull origin main'
```

## 🚨 禁止事項
- **機密情報コミット禁止**: パスワード・APIキー等
- **直接本番変更禁止**: 必ずGitHub経由で変更
- **テスト省略禁止**: 動作確認なしでのデプロイ禁止
