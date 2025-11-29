"""
AI関連モジュール
"""

from app.ai.openai_client import OpenAIClient
from app.ai.embeddings import generate_embedding, generate_faq_embedding
from app.ai.vector_search import search_similar_faqs, search_similar_patterns
from app.ai.engine import RAGChatEngine
from app.ai.confidence import calculate_confidence
from app.ai.prompts import RAG_SYSTEM_PROMPT, build_rag_prompt
from app.ai.safety_check import check_safety_category, MEDICAL_KEYWORDS, SAFETY_KEYWORDS
from app.ai.fallback import get_fallback_message, FALLBACK_MESSAGES

__all__ = [
    "OpenAIClient",
    "generate_embedding",
    "generate_faq_embedding",
    "search_similar_faqs",
    "search_similar_patterns",
    "RAGChatEngine",
    "calculate_confidence",
    "RAG_SYSTEM_PROMPT",
    "build_rag_prompt",
    "check_safety_category",
    "MEDICAL_KEYWORDS",
    "SAFETY_KEYWORDS",
    "get_fallback_message",
    "FALLBACK_MESSAGES",
]

