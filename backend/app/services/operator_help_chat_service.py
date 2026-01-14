"""
事業者向けAIヘルプチャットサービス
OpenAI GPT-4o-miniを使用した対話型ヘルプ
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.operator_faq_service import OperatorFaqService
from app.ai.openai_client import OpenAIClient
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OperatorHelpChatService:
    """事業者向けAIヘルプチャットサービス"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.faq_service = OperatorFaqService(db)
        self.openai_client = OpenAIClient()
        self.max_tokens = 500
        self.temperature = 0.7
    
    async def process_message(
        self,
        message: str,
        language: str = 'ja',
        operator_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        チャットメッセージ処理
        
        Args:
            message: ユーザーメッセージ
            language: 言語コード
            operator_id: 事業者ID (ログ用)
        
        Returns:
            {
                'response': AI回答文,
                'related_faqs': 関連FAQ IDリスト,
                'related_url': 関連URL,
                'timestamp': タイムスタンプ
            }
        """
        try:
            # 全FAQを取得
            all_faqs = await self.faq_service.get_faqs(language=language)
            
            # システムプロンプト構築
            system_prompt = self._build_system_prompt(all_faqs, language)
            
            # ユーザーメッセージとシステムプロンプトを結合
            full_prompt = f"{system_prompt}\n\nユーザーの質問: {message}"
            
            # OpenAI API呼び出し
            ai_response = await self.openai_client.generate_response(
                prompt=full_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                language=language
            )
            
            # 関連FAQを検索
            related_faqs = await self._find_related_faqs(message, all_faqs)
            
            # 関連URLを抽出
            related_url = self._extract_related_url(ai_response, all_faqs)
            
            response_data = {
                'response': ai_response,
                'related_faqs': [faq['id'] for faq in related_faqs[:3]],
                'related_url': related_url,
                'timestamp': self._get_current_timestamp()
            }
            
            logger.info(f"Help chat processed: operator_id={operator_id}, message_len={len(message)}")
            return response_data
        
        except Exception as e:
            logger.error(f"Help chat error: {str(e)}", exc_info=True)
            return {
                'response': self._get_error_message(language),
                'related_faqs': [],
                'related_url': None,
                'timestamp': self._get_current_timestamp()
            }
    
    def _build_system_prompt(self, faqs: List[Dict[str, Any]], language: str) -> str:
        """
        システムプロンプト構築
        
        Args:
            faqs: FAQ辞書のリスト
            language: 言語コード
        
        Returns:
            システムプロンプト文字列
        """
        if language == 'ja':
            base_prompt = """あなたはYadOPERA（宿泊施設管理システム）のヘルプアシスタントです。
宿泊事業者（管理者）からの質問に対して、以下のFAQデータベースを参照して回答してください。

# 回答ガイドライン
1. 簡潔で分かりやすい回答を心がける
2. 該当するFAQがある場合は、その内容を元に回答する
3. 関連する管理画面のURLを案内する
4. FAQに該当しない質問の場合は、サポートへの問い合わせを案内する
5. 回答は300文字以内に収める

# FAQ データベース

"""
        else:
            base_prompt = """You are a help assistant for YadOPERA (accommodation management system).
Answer questions from accommodation operators (administrators) based on the following FAQ database.

# Response Guidelines
1. Keep responses concise and clear
2. Base answers on relevant FAQs
3. Provide related admin page URLs
4. Direct to support for non-FAQ questions
5. Limit responses to 300 characters

# FAQ Database

"""
        
        # FAQ全文を追加
        for faq in faqs:
            faq_text = f"""
## {faq['category']} - {faq['question']}
回答: {faq['answer']}
関連URL: {faq.get('related_url', 'なし')}
---
"""
            base_prompt += faq_text
        
        return base_prompt
    
    async def _find_related_faqs(
        self,
        query: str,
        all_faqs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        関連FAQ検索
        
        Args:
            query: 検索クエリ
            all_faqs: 全FAQリスト
        
        Returns:
            関連FAQリスト
        """
        related = []
        query_lower = query.lower()
        
        for faq in all_faqs:
            score = 0.0
            
            # 質問文に部分一致
            if query_lower in faq['question'].lower():
                score += 1.0
            
            # キーワードに部分一致
            if faq.get('keywords') and query_lower in faq['keywords'].lower():
                score += 0.7
            
            # 回答文に部分一致
            if query_lower in faq['answer'].lower():
                score += 0.3
            
            if score > 0:
                faq_copy = faq.copy()
                faq_copy['relevance_score'] = score
                related.append(faq_copy)
        
        # スコア順にソート
        related.sort(key=lambda x: x['relevance_score'], reverse=True)
        return related
    
    def _extract_related_url(
        self,
        ai_response: str,
        all_faqs: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        AI回答から関連URLを抽出
        
        Args:
            ai_response: AI回答文
            all_faqs: 全FAQリスト
        
        Returns:
            関連URL (見つからない場合None)
        """
        # AI回答に含まれるURLキーワードを検索
        for faq in all_faqs:
            if faq.get('related_url') and (
                faq['question'] in ai_response or
                faq['category'] in ai_response
            ):
                return faq['related_url']
        
        return None
    
    def _get_error_message(self, language: str) -> str:
        """
        エラーメッセージ取得
        
        Args:
            language: 言語コード
        
        Returns:
            エラーメッセージ
        """
        if language == 'ja':
            return "申し訳ございません。一時的にエラーが発生しました。しばらく待ってから再度お試しいただくか、サポート（support@yadopera.com）までお問い合わせください。"
        else:
            return "We apologize for the inconvenience. A temporary error has occurred. Please try again later or contact support at support@yadopera.com."
    
    def _get_current_timestamp(self) -> str:
        """現在のタイムスタンプ取得"""
        return datetime.utcnow().isoformat() + 'Z'

