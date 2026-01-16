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
from app.core.plan_limits import filter_faq_presets_by_plan
from fastapi import HTTPException, status, BackgroundTasks
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def convert_subscription_plan_to_plan_type(subscription_plan: str) -> str:
    """
    subscription_planをplan_typeに変換
    
    Args:
        subscription_plan: 料金プラン（'free', 'mini', 'small', 'standard', 'premium'）
    
    Returns:
        plan_type: プラン種別（'Free', 'Mini', 'Small', 'Standard', 'Premium'）
    """
    plan_mapping = {
        'free': 'Free',
        'mini': 'Mini',
        'small': 'Small',
        'standard': 'Standard',
        'premium': 'Premium'
    }
    return plan_mapping.get(subscription_plan.lower(), 'Free')


def get_plan_defaults(plan_type: str) -> dict:
    """
    プラン種別に応じたデフォルト値を取得
    
    Args:
        plan_type: プラン種別（'Free', 'Mini', 'Small', 'Standard', 'Premium'）
    
    Returns:
        プラン別デフォルト値（monthly_question_limit, faq_limit, language_limit）
    """
    defaults = {
        'Free': {
            'monthly_question_limit': 30,
            'faq_limit': 20,
            'language_limit': 1
        },
        'Mini': {
            'monthly_question_limit': None,  # 無制限
            'faq_limit': 20,
            'language_limit': 1
        },
        'Small': {
            'monthly_question_limit': 200,
            'faq_limit': 20,
            'language_limit': 1
        },
        'Standard': {
            'monthly_question_limit': 500,
            'faq_limit': 20,
            'language_limit': 1
        },
        'Premium': {
            'monthly_question_limit': 1000,
            'faq_limit': None,  # 無制限
            'language_limit': None  # 無制限
        }
    }
    return defaults.get(plan_type, defaults['Free'])


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
    async def register_facility_sync(
        db: AsyncSession,
        request: FacilityRegisterRequest
    ) -> LoginResponse:
        """
        施設登録処理（同期部分：施設・ユーザー作成のみ）
        
        Args:
            db: データベースセッション
            request: 施設登録リクエスト
        
        Returns:
            ログインレスポンス（JWTトークン含む）
        
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
        
        # プラン情報を変換・設定
        plan_type = convert_subscription_plan_to_plan_type(request.subscription_plan)
        plan_defaults = get_plan_defaults(plan_type)
        
        # 施設作成
        facility = Facility(
            name=request.facility_name,
            slug=await AuthService._generate_unique_slug(db, request.facility_name),
            email=request.email,
            subscription_plan=request.subscription_plan,
            plan_type=plan_type,
            monthly_question_limit=plan_defaults['monthly_question_limit'],
            faq_limit=plan_defaults['faq_limit'],
            language_limit=plan_defaults['language_limit']
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
        
        # コミット（施設・ユーザー作成を確定）
        await db.commit()
        
        # JWTトークン生成
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

    @staticmethod
    async def register_facility_async_faqs(
        facility_id: int,
        user_id: int,
        subscription_plan: str
    ):
        """
        FAQ自動投入処理（バックグラウンド実行）
        
        Args:
            facility_id: 施設ID
            user_id: ユーザーID
            subscription_plan: 料金プラン
        """
        from app.database import AsyncSessionLocal
        from app.data.faq_presets import FAQ_PRESETS
        from app.schemas.faq import FAQRequest
        from app.core.cache import delete_cache_pattern
        
        # 新しいデータベースセッションを作成
        async with AsyncSessionLocal() as db:
            try:
                # 料金プランに基づいてFAQプリセットをフィルタ
                filtered_presets = filter_faq_presets_by_plan(
                    FAQ_PRESETS,
                    subscription_plan
                )
                
                # プリセットFAQをFAQRequestに変換
                faq_requests = []
                for preset in filtered_presets:
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
                
                # FAQ一括作成
                await FAQService(db).bulk_create_faqs(facility_id, faq_requests, user_id)
                await db.commit()
                
                # キャッシュを無効化（FAQ作成後、最新のデータが取得されるようにする）
                try:
                    deleted_count = await delete_cache_pattern(f"faq:list:*facility_id={facility_id}*")
                    logger.info(
                        f"FAQ cache invalidated: {deleted_count} keys deleted "
                        f"(facility_id={facility_id})"
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to invalidate FAQ cache: facility_id={facility_id}, "
                        f"error={str(e)}",
                        exc_info=True
                    )
                    # エラーが発生しても処理は続行（キャッシュは次回のリクエストで更新される）
                
                logger.info(
                    f"Background FAQ creation completed: facility_id={facility_id}, "
                    f"plan={subscription_plan}, count={len(faq_requests)}"
                )
                
                # バックグラウンド処理完了後、5秒待ってから再度キャッシュを無効化
                # これにより、バックグラウンド処理完了直後に取得されたキャッシュも無効化される
                import asyncio
                await asyncio.sleep(5)
                
                try:
                    deleted_count = await delete_cache_pattern(f"faq:list:*facility_id={facility_id}*")
                    logger.info(
                        f"FAQ cache invalidated (delayed): {deleted_count} keys deleted "
                        f"(facility_id={facility_id})"
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to invalidate FAQ cache (delayed): facility_id={facility_id}, "
                        f"error={str(e)}",
                        exc_info=True
                    )
                    # エラーが発生しても処理は続行
            except Exception as e:
                logger.error(
                    f"Background FAQ creation failed: facility_id={facility_id}, "
                    f"plan={subscription_plan}, error={str(e)}",
                    exc_info=True
                )
                # エラーが発生してもロールバックは不要（既に施設・ユーザーは作成済み）

    @staticmethod
    async def register_facility(
        db: AsyncSession,
        request: FacilityRegisterRequest,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> LoginResponse:
        """
        施設登録処理（FAQ自動投入は非同期で実行）
        
        Args:
            db: データベースセッション
            request: 施設登録リクエスト
            background_tasks: バックグラウンドタスク（オプション）
        
        Returns:
            ログインレスポンス（JWTトークン含む）
        
        Raises:
            HTTPException: 登録失敗時
        """
        # 施設・ユーザー作成（同期処理）
        response = await AuthService.register_facility_sync(db, request)
        
        # FAQ自動投入をバックグラウンドで実行
        if background_tasks:
            # FastAPIのBackgroundTasksは非同期関数を直接実行できる
            background_tasks.add_task(
                AuthService.register_facility_async_faqs,
                response.user.facility_id,
                response.user.id,
                request.subscription_plan
            )
        else:
            # バックグラウンドタスクが利用できない場合は同期的に実行（後方互換性）
            logger.warning(
                "BackgroundTasks not available, running FAQ creation synchronously"
            )
            await AuthService.register_facility_async_faqs(
                response.user.facility_id,
                response.user.id,
                request.subscription_plan
            )
        
        return response

