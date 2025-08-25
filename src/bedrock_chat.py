"""
Bedrock チャット機能
Amazon Bedrock Claude 3を使用したチャット機能
"""

import boto3
import json
import logging
from typing import Dict, List, Optional
from fastapi import HTTPException
from datetime import datetime

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BedrockChatService:
    def __init__(self, region_name: str = "us-east-1"):
        """
        Bedrockチャットサービスの初期化
        """
        self.region_name = region_name
        self.bedrock_client = None
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        
    def _get_bedrock_client(self):
        """Bedrockクライアントを取得"""
        if not self.bedrock_client:
            try:
                self.bedrock_client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=self.region_name
                )
                logger.info(f"Bedrock client initialized for region: {self.region_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Bedrock client: {e}")
                raise HTTPException(status_code=500, detail="Bedrock client initialization failed")
        return self.bedrock_client
    
    def _prepare_system_prompt(self, customer_context: Optional[Dict] = None) -> str:
        """システムプロンプトを準備"""
        base_prompt = """あなたは金融アドバイザーのアシスタントです。
顧客の資産管理や投資に関する質問に、専門的で親切に回答してください。

以下の点を心がけてください：
- 正確で実用的な情報を提供する
- リスクについて適切に説明する
- 個別の投資アドバイスではなく、一般的な情報として回答する
- 日本語で回答する
- 専門用語は分かりやすく説明する"""

        if customer_context:
            context_info = f"""

現在の顧客情報：
- 顧客名: {customer_context.get('name', 'N/A')}
- 年齢: {customer_context.get('age', 'N/A')}
- 投資経験: {customer_context.get('investment_experience', 'N/A')}
- リスク許容度: {customer_context.get('risk_tolerance', 'N/A')}
- 総資産: {customer_context.get('total_assets', 'N/A')}円

この顧客情報を参考にして、より個別化された回答を提供してください。"""
            base_prompt += context_info
            
        return base_prompt
    
    async def chat(
        self, 
        message: str, 
        conversation_history: List[Dict] = None,
        customer_context: Optional[Dict] = None
    ) -> Dict:
        """
        Bedrockを使用してチャット応答を生成
        """
        try:
            client = self._get_bedrock_client()
            
            # システムプロンプトを準備
            system_prompt = self._prepare_system_prompt(customer_context)
            
            # 会話履歴を構築
            messages = []
            
            if conversation_history:
                for item in conversation_history[-10:]:  # 最新10件のみ
                    messages.append({
                        "role": "user",
                        "content": item.get("user_message", "")
                    })
                    messages.append({
                        "role": "assistant", 
                        "content": item.get("assistant_message", "")
                    })
            
            # 現在のメッセージを追加
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Bedrock APIリクエストボディを構築
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "system": system_prompt,
                "messages": messages,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            # Bedrock APIを呼び出し
            response = client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType='application/json',
                accept='application/json'
            )
            
            # レスポンスを解析
            response_body = json.loads(response['body'].read())
            assistant_message = response_body['content'][0]['text']
            
            # 使用量情報を取得
            usage = response_body.get('usage', {})
            
            result = {
                "message": assistant_message,
                "timestamp": datetime.now().isoformat(),
                "model": self.model_id,
                "usage": {
                    "input_tokens": usage.get('input_tokens', 0),
                    "output_tokens": usage.get('output_tokens', 0)
                }
            }
            
            logger.info(f"Chat response generated successfully. Tokens used: {usage}")
            return result
            
        except Exception as e:
            logger.error(f"Error in chat generation: {e}")
            raise HTTPException(
                status_code=500, 
                detail=f"チャット応答の生成に失敗しました: {str(e)}"
            )

# グローバルインスタンス
bedrock_chat_service = BedrockChatService()
