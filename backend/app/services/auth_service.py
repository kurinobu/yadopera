"""
認証サービス
認証ビジネスロジック
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.models.user import User
from app.models.facility import Facility
from app.core.security import verify_password, hash_password
from app.core.jwt import create_access_token
from app.core.config import settings
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse, FacilityRegisterRequest
from app.schemas.faq import FAQRequest
from app.services.faq_service import FAQService
from app.data.faq_presets import FAQ_PRESETS
from fastapi import HTTPException, status
from typing import Optional


class AuthService:
    """
    認証サービス
    """
    
    @staticmethod
    async def _generate_unique_slug(db: AsyncSession, base_name: str) -> str:
        """
        URLセーフなユニークslugを生成
        
        Args:
            db: データベースセッション
            base_name: 施設名
        
        Returns:
            str: ユニークなslug
        """
        import uuid
        import re
        
        # 施設名を英数字に変換（日本語は削除）
        slug_base = re.sub(r'[^\w\s-]', '', base_name.lower())
        slug_base = re.sub(r'[-\s]+', '-', slug_base).strip('-')
        
        # 英数字が存在しない場合はデフォルト値を使用
        if not slug_base or len(slug_base) < 1:
            slug_base = "facility"
        
        # 最大20文字に制限
        slug_base = slug_base[:20]
        
        # UUIDの先頭8文字を付与
        unique_id = str(uuid.uuid4())[:8]
        slug = f"{slug_base}-{unique_id}"
        
        # 念のため重複チェック（UUID使用時はほぼ不要だが安全のため）
        result = await db.execute(
            select(Facility).where(Facility.slug == slug)
        )
        if result.scalar_one_or_none() is not None:
            # 万が一重複した場合はUUID全体を使用
            slug = f"{slug_base}-{str(uuid.uuid4())}"
        
        return slug
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        login_data: LoginRequest
    ) -> Optional[User]:
        """
        ユーザー認証
        
        Args:
            db: データベースセッション
            login_data: ログインリクエストデータ
            
        Returns:
            認証されたユーザー（認証失敗時はNone）
        """
        # ユーザー取得
        result = await db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            return None
        
        # パスワード検証
        if not verify_password(login_data.password, user.password_hash):
            return None
        
        # アクティブユーザーか確認
        if not user.is_active:
            return None
        
        return user
    
    @staticmethod
    async def login(
        db: AsyncSession,
        login_data: LoginRequest
    ) -> LoginResponse:
        """
        ログイン処理
        
        Args:
            db: データベースセッション
            login_data: ログインリクエストデータ
            
        Returns:
            ログインレスポンス
            
        Raises:
            HTTPException: 認証失敗時
        """
        # ユーザー認証
        user = await AuthService.authenticate_user(db, login_data)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 最終ログイン時刻更新
        user.last_login_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        
        # JWTトークン生成
        # JWT仕様（RFC 7519）に準拠: subフィールドは文字列であるべき
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        # レスポンス作成
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,  # 秒単位
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                facility_id=user.facility_id,
                is_active=user.is_active,
            )
        )
    
    @staticmethod
    async def logout(
        db: AsyncSession,
        user: User
    ) -> dict:
        """
        ログアウト処理（JWTは無効化しない、クライアント側で削除）
        
        Args:
            db: データベースセッション
            user: ユーザー
            
        Returns:
            ログアウトレスポンス
        """
        # JWTはステートレスなので、サーバー側での無効化は不要
        # 必要に応じてRedisに無効化リストを保存することも可能
        return {"message": "Logged out successfully"}
    
    @staticmethod
    async def register_facility(
        db: AsyncSession,
        request: FacilityRegisterRequest
    ) -> LoginResponse:
        """
        施設登録処理
        
        Args:
            db: データベースセッション
            request: 施設登録リクエスト
            
        Returns:
            ログインレスポンス（自動ログイン）
            
        Raises:
            HTTPException: 登録失敗時
        """
        # メールアドレス重複チェック
        result = await db.execute(
            select(User).where(User.email == request.email)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # トランザクション開始
        # async with db.begin():
        # 施設作成
        facility = Facility(
            name=request.facility_name,
            slug=await AuthService._generate_unique_slug(db, request.facility_name),
            email=request.email,
            subscription_plan=request.subscription_plan
        )
        db.add(facility)
        await db.flush()  # facility_idを取得
        
        # ユーザー作成
        user = User(
            facility_id=facility.id,
            email=request.email,
            password_hash=hash_password(request.password),
            role="owner",
            full_name=None,
            is_active=True
        )
        db.add(user)
        await db.flush()  # user_idを取得
        
        # FAQ自動投入
        try:
            # プリセットFAQをFAQRequestに変換
            faq_requests = []
            for preset in FAQ_PRESETS:
                faq_request = FAQRequest(
                    category=preset["category"],
                    intent_key=preset["intent_key"],
                    translations=[
                        {
                            "language": t["language"],
                            "question": t["question"],
                            "answer": t["answer"]
                        } for t in preset["translations"]
                    ],
                    priority=preset["priority"],
                    is_active=True
                )
                faq_requests.append(faq_request)
            
            await FAQService(db).bulk_create_faqs(facility.id, faq_requests, user.id)
        except Exception as e:
            # FAQ投入失敗時はロールバック
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create FAQs: {str(e)}"
            )
        
        await db.commit()
        
        # コミット完了後、JWTトークン生成
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        # レスポンス作成
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                facility_id=user.facility_id,
                is_active=user.is_active,
            )
        )

