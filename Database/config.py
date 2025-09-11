# Database Management Configuration

# 複数データベース設定
DATABASES = {
    'wealthai': {
        'name': 'WealthAI Database',
        'description': '顧客管理・保有商品データ',
        'host': 'localhost',
        'port': 5432,
        'database': 'wealthai',
        'user': 'wealthai_user',
        'password': 'wealthai123'
    },
    'productmaster': {
        'name': 'ProductMaster Database', 
        'description': '商品マスターデータ',
        'host': 'localhost',
        'port': 5432,
        'database': 'productmaster',
        'user': 'productmaster_user',
        'password': 'productmaster123'
    },
    'aichat': {
        'name': 'AIChat Database',
        'description': 'システムプロンプト管理',
        'host': 'localhost',
        'port': 5432,
        'database': 'aichat',
        'user': 'aichat_user',
        'password': 'aichat123'
    }
}

# サーバー設定
SERVER_CONFIG = {
    "title": "Database Management System",
    "version": "2.0.0",
    "port": 8006
}
