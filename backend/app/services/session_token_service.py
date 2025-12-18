"""
セッション統合トークンサービス（v0.3新規）
"""

import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, any_
from app.models.session_token import SessionToken
from app.models.conversation import Conversation
from fastapi import HTTPException, status


class SessionTokenService:
    """
    セッション統合トークン管理サービス（v0.3新規）
    """
    
    TOKEN_LENGTH = 4
    TOKEN_CHARS = string.ascii_uppercase + string.digits  # A-Z, 0-9
    MAX_RETRY = 10  # 重複時の最大再試行回数
    
    async def generate_token(
        self,
        facility_id: int,
        primary_session_id: str,
        db: AsyncSession
    ) -> str:
        """
        セッション統合トークン生成（v0.3新規）
        - 4桁英数字ランダム生成
        - 重複チェック（UNIQUE制約）
        - 最大10回再試行
        - 会話が存在しない場合は会話を作成する（2025-12-18追加）
        
        Args:
            facility_id: 施設ID
            primary_session_id: プライマリセッションID
            db: データベースセッション
            
        Returns:
            生成されたトークン（4桁英数字）
            
        Raises:
            ValueError: 最大再試行回数に達した場合
        """
        # プライマリセッションIDの存在確認
        result = await db.execute(
            select(Conversation).where(Conversation.session_id == primary_session_id)
        )
        conversation = result.scalar_one_or_none()
        
        # 会話が存在しない場合は新規作成（2025-12-18追加）
        if conversation is None:
            conversation = Conversation(
                facility_id=facility_id,
                session_id=primary_session_id,
                guest_language="en",  # デフォルト言語（後でメッセージ送信時に更新可能）
                started_at=datetime.utcnow(),
                last_activity_at=datetime.utcnow()
            )
            db.add(conversation)
            await db.flush()
            await db.refresh(conversation)
        
        if conversation.facility_id != facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Session does not belong to this facility"
            )
        
        # トークン生成（重複チェック付き）
        for attempt in range(self.MAX_RETRY):
            # ランダム4桁英数字生成
            token = ''.join(random.choices(self.TOKEN_CHARS, k=self.TOKEN_LENGTH))
            
            # 重複チェック
            result = await db.execute(
                select(SessionToken).where(SessionToken.token == token)
            )
            existing = result.scalar_one_or_none()
            
            if existing is None:
                # 重複なし → トークン作成
                expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
                
                session_token = SessionToken(
                    facility_id=facility_id,
                    token=token,
                    primary_session_id=primary_session_id,
                    expires_at=expires_at
                )
                
                db.add(session_token)
                await db.commit()
                await db.refresh(session_token)
                
                return token
        
        # 最大再試行回数に達した場合（極めて稀）
        raise ValueError("Failed to generate unique token after maximum retries")
    
    async def link_session(
        self,
        facility_id: int,
        token: str,
        new_session_id: str,
        db: AsyncSession
    ) -> SessionToken:
        """
        セッション統合（v0.3新規）
        - トークン検証
        - 有効期限チェック
        - セッションIDをlinked_session_idsに追加
        
        Args:
            facility_id: 施設ID
            token: セッション統合トークン
            new_session_id: 統合する新しいセッションID
            db: データベースセッション
            
        Returns:
            更新されたSessionTokenオブジェクト
            
        Raises:
            HTTPException: トークンが無効または期限切れの場合
        """
        # トークン検索
        result = await db.execute(
            select(SessionToken).where(SessionToken.token == token)
        )
        token_obj = result.scalar_one_or_none()
        
        if not token_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid token"
            )
        
        # 施設IDチェック
        if token_obj.facility_id != facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token does not belong to this facility"
            )
        
        # 有効期限チェック
        if token_obj.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token expired"
            )
        
        # 新しいセッションIDの存在確認
        result = await db.execute(
            select(Conversation).where(Conversation.session_id == new_session_id)
        )
        new_conversation = result.scalar_one_or_none()
        
        if new_conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New session not found"
            )
        
        if new_conversation.facility_id != facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="New session does not belong to this facility"
            )
        
        # セッションIDをlinked_session_idsに追加（重複チェック）
        if token_obj.linked_session_ids is None:
            token_obj.linked_session_ids = []
        
        if new_session_id not in token_obj.linked_session_ids:
            # SQLAlchemyの変更追跡を確実にするため、新しいリストを代入
            linked_ids = list(token_obj.linked_session_ids) if token_obj.linked_session_ids else []
            linked_ids.append(new_session_id)
            token_obj.linked_session_ids = linked_ids
            await db.commit()
            await db.refresh(token_obj)
        
        return token_obj
    
    async def verify_token(
        self,
        token: str,
        db: AsyncSession
    ) -> Optional[SessionToken]:
        """
        トークン検証
        
        Args:
            token: セッション統合トークン
            db: データベースセッション
            
        Returns:
            SessionTokenオブジェクト（無効な場合はNone）
        """
        result = await db.execute(
            select(SessionToken).where(SessionToken.token == token)
        )
        token_obj = result.scalar_one_or_none()
        
        if not token_obj:
            return None
        
        # 有効期限チェック
        if token_obj.expires_at < datetime.now(timezone.utc):
            return None
        
        return token_obj
    
    async def get_token_by_session_id(
        self,
        session_id: str,
        db: AsyncSession
    ) -> Optional[SessionToken]:
        """
        セッションIDからトークンを取得
        
        Args:
            session_id: セッションID
            db: データベースセッション
            
        Returns:
            SessionTokenオブジェクト（見つからない場合はNone）
        """
        # プライマリセッションIDまたはリンクされたセッションIDで検索
        result = await db.execute(
            select(SessionToken).where(
                or_(
                    SessionToken.primary_session_id == session_id,
                    session_id == any_(SessionToken.linked_session_ids)
                )
            )
        )
        return result.scalar_one_or_none()

