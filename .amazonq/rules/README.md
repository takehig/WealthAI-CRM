# WealthAI Enterprise Systems

金融商品管理とAI対話機能を統合したエンタープライズシステム

## 🏗️ システム構成

### サービス一覧
| サービス | ポート | URL | 説明 |
|---------|--------|-----|------|
| **Portal** | 80 | http://44.217.45.24/ | 統合エントランス |
| **CRM** | 8000 | http://44.217.45.24/crm/ | 顧客管理・Bedrock チャット |
| **ProductMaster** | 8001 | http://44.217.45.24/products/ | 商品情報管理 |
| **AIChat** | 8002 | http://44.217.45.24/aichat/ | AI対話・MCP統合 |
| **ProductMaster MCP** | 8003 | http://44.217.45.24/mcp/products/ | 商品検索MCP サーバー |

### アーキテクチャ
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend       │    │   MCP Servers   │
│                 │    │                  │    │                 │
│ ProductMaster   │◄──►│   MCPManager     │◄──►│ ProductMaster   │
│ MCP Button      │    │                  │    │ (Port 8003)     │
│                 │    │   AIAgent        │    │                 │
│ [Future MCPs]   │    │                  │    │ [Future MCPs]   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 VSCode での開発

### 推奨拡張機能
- Amazon Q Developer
- Python
- Pylint
- Prettier

### 開発タスク
- `Ctrl+Shift+P` → `Tasks: Run Task`
  - **Start All Services**: 全サービス起動
  - **Stop All Services**: 全サービス停止
  - **Check Services Status**: サービス状態確認
  - **MCP Health Check**: MCP診断

### デバッグ
- `F5` でデバッグ開始
- 各サービス個別にデバッグ可能

## 🛠️ 開発環境セットアップ

### 前提条件
- Python 3.9+
- Node.js 16+ (フロントエンド開発時)
- PostgreSQL
- AWS CLI設定済み

### ローカル開発
```bash
# プロジェクトクローン
git clone https://github.com/takehig/WealthAI-CRM
git clone https://github.com/takehig/AIChat-System
git clone https://github.com/takehig/ProductMaster-System
git clone https://github.com/takehig/ProductMaster-MCP
git clone https://github.com/takehig/enterprise-systemd

# 依存関係インストール
cd CRM && pip install -r requirements.txt
cd ../AIChat/backend && pip install -r requirements.txt
cd ../../ProductMaster && pip install -r requirements.txt
cd ../ProductMaster-MCP && pip install -r requirements.txt
```

## 🔧 運用管理

### サービス管理
```bash
# 全サービス管理
./enterprise-systemd/scripts/manage-services.sh start|stop|restart|status

# 個別サービス
sudo systemctl start|stop|restart wealthai-crm
sudo systemctl start|stop|restart productmaster
sudo systemctl start|stop|restart aichat
sudo systemctl start|stop|restart productmaster-mcp
```

### MCP診断
```bash
# WSL環境から
./enterprise-systemd/scripts/mcp-check-wsl.sh

# EC2環境で
./enterprise-systemd/scripts/mcp-check.sh
```

## 📋 MCP拡張

### 新しいMCP追加手順
1. **MCPサーバー作成**: 新しいポートで起動
2. **MCPManager更新**: `AIChat/backend/mcp_manager.py`
3. **設定追加**:
```python
'new_mcp': {
    'name': 'NewMCP',
    'description': '新しいMCP機能',
    'url': 'http://localhost:8004',
    'enabled': False
}
```

## 🐛 トラブルシューティング

### よくある問題
- **MCP読み込み中**: JavaScript APIパス問題 → 絶対パス使用
- **文字化け**: CSV文字エンコーディング → UTF-8 BOM使用
- **サービス起動失敗**: Python構文エラー → ログ確認

### デバッグ手順
1. ブラウザ開発者ツール → Console確認
2. `[MCP DEBUG]` ログ確認
3. サービスログ確認: `journalctl -u <service> -f`
4. API直接テスト: `curl http://localhost:<port>/api/status`

## 📚 ドキュメント

- [MCP設計書](./docs/MCP_Architecture_Design.md)
- [Context使用ガイド](./docs/Context_Usage_Guide.md)
- [API仕様書](./docs/API_Specification.md)

## 🔗 関連リンク

- [Amazon Q Developer](https://aws.amazon.com/q/developer/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 📝 更新履歴

- **2025-08-30**: VSCode対応、MCP拡張アーキテクチャ実装完了
- **2025-08-28**: 各システム統合完了
- **2025-08-26**: プロジェクト開始
