"""
ProductMaster System API呼び出しサービス
"""

import httpx
import os
from typing import List, Dict, Optional
from datetime import datetime

class ProductMasterService:
    """ProductMaster System APIクライアント"""
    
    def __init__(self):
        self.base_url = os.getenv("PRODUCT_MASTER_URL", "http://localhost:8001")
        self.api_token = os.getenv("PRODUCT_MASTER_TOKEN", "demo-token-12345")
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    async def get_products(self, limit: int = 100, category_code: Optional[str] = None) -> List[Dict]:
        """商品一覧を取得"""
        try:
            params = {"limit": limit}
            if category_code:
                params["category_code"] = category_code
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/products/",
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error fetching products: {e}")
            return []
    
    async def get_product(self, product_id: int) -> Optional[Dict]:
        """商品詳細を取得"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/products/{product_id}",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error fetching product {product_id}: {e}")
            return None
    
    async def search_products(self, query: str, category_code: Optional[str] = None, 
                            risk_level: Optional[int] = None) -> Dict:
        """商品検索"""
        try:
            params = {"q": query}
            if category_code:
                params["category_code"] = category_code
            if risk_level:
                params["risk_level"] = risk_level
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/products/search",
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error searching products: {e}")
            return {"products": [], "total": 0, "page": 1, "size": 20, "pages": 0}
    
    async def get_similar_products(self, product_id: int, limit: int = 5) -> List[Dict]:
        """類似商品を取得"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/products/{product_id}/similar",
                    headers=self.headers,
                    params={"limit": limit},
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error fetching similar products for {product_id}: {e}")
            return []
    
    async def get_latest_price(self, product_id: int) -> Optional[Dict]:
        """最新価格を取得"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/prices/{product_id}/latest",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error fetching latest price for product {product_id}: {e}")
            return None
    
    async def get_categories(self) -> List[Dict]:
        """商品カテゴリ一覧を取得"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/categories/",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return []

# シングルトンインスタンス
product_service = ProductMasterService()
