"""
認証サービス
認証ビジネスロジック
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from app.models.user import User
from app.models.facility import Facility
from app.core.security import verify_password, hash_password
from app.core.jwt import create_access_token
from app.core.config import settings
from app.schemas.auth import (
    LoginRequest, LoginResponse, UserResponse,
    FacilityRegisterRequest, FacilityRegisterResponse,
    VerifyEmailRequest, VerifyEmailResponse,
    ResendVerificationRequest, ResendVerificationResponse,
    PasswordResetResponse
)
from app.schemas.faq import FAQRequest
from app.services.faq_service import FAQService
from app.services.email_service import EmailService
from app.services.notification_service import notify_admin_email_failure
from app.services import stripe_service
from app.data.faq_presets import FAQ_PRESETS
from app.core.plan_limits import filter_faq_presets_by_plan
from fastapi import HTTPException, status, BackgroundTasks, Request
from typing import Optional
import logging
import uuid

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
    
    注意: faq_limit/language_limit は plan_limits.py の PLAN_FAQ_LIMITS と一致させる（CSV一括登録 Phase 0）
    """
    defaults = {
        'Free': {
            'monthly_question_limit': 30,
            'faq_limit': 20,
            'language_limit': 1  # ["ja"]
        },
        'Mini': {
            'monthly_question_limit': None,  # 無制限
            'faq_limit': 30,
            'language_limit': 2  # ["ja", "en"]
        },
        'Small': {
            'monthly_question_limit': 200,
            'faq_limit': 50,
            'language_limit': 3  # ["ja", "en", "zh-TW"]
        },
        'Standard': {
            'monthly_question_limit': 500,
            'faq_limit': 100,
            'language_limit': 4  # ["ja", "en", "zh-TW", "fr"]
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
        
        # メールアドレス確認済みか確認
        if not user.email_verified:
            return None
        
        return user
    
    @staticmethod
    async def login(
        db: AsyncSession,
        login_data: LoginRequest,
        request: Optional["Request"] = None
    ) -> LoginResponse:
        """
        ログイン処理
        
        Args:
            db: データベースセッション
            login_data: ログインリクエストデータ
            request: リクエストオブジェクト（IPアドレス、User-Agent取得用）
            
        Returns:
            ログインレスポンス
            
        Raises:
            HTTPException: 認証失敗時
        """
        # ユーザー認証
        user = await AuthService.authenticate_user(db, login_data)
        
        if user is None:
            # 🟠 メールアドレス未確認の場合の詳細エラー（日本語・英語併記）
            result = await db.execute(
                select(User).where(User.email == login_data.email)
            )
            existing_user = result.scalar_one_or_none()
            # エラーログで施設紐づけするため request.state に保持
            if request and existing_user and getattr(existing_user, "facility_id", None) is not None:
                request.state.facility_id = existing_user.facility_id

            if existing_user and not existing_user.email_verified:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "メールアドレスが確認されていません。"
                        "登録時に送信された確認メールをご確認ください。"
                        "メールが届いていない場合は、確認メール再送信をご利用ください。"
                        "\n\n"
                        "Email address not verified. "
                        "Please check your email and verify your account. "
                        "If you didn't receive the email, please use the resend function."
                    ),
                )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 最終ログイン時刻更新
        user.last_login_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(user)
        
        # 管理者ログインログ記録（非同期）
        if request:
            from app.models.admin_activity_log import AdminActivityLog
            activity_log = AdminActivityLog(
                user_id=user.id,
                facility_id=user.facility_id,
                action_type="login",
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent")
            )
            db.add(activity_log)
            await db.commit()
        
        # JWTトークン生成
        # JWT仕様（RFC 7519）に準拠: subフィールドは文字列であるべき
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        
        # 初回ログイン時やることリストモーダル表示要否（施設の onboarding_modal_shown_at が NULL なら True）
        facility_result = await db.execute(select(Facility).where(Facility.id == user.facility_id))
        facility = facility_result.scalar_one_or_none()
        show_onboarding_modal = facility is not None and facility.onboarding_modal_shown_at is None
        
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
                email_verified=user.email_verified,  # ★追加
                show_onboarding_modal=show_onboarding_modal,
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
    ) -> tuple[User, Facility]:
        """
        施設登録処理（同期部分：施設・ユーザー作成のみ）
        
        Args:
            db: データベースセッション
            request: 施設登録リクエスト
        
        Returns:
            (User, Facility): 作成されたユーザーと施設
        
        Raises:
            HTTPException: 登録失敗時
        """
        # メールアドレス重複チェック
        result = await db.execute(
            select(User).where(User.email == request.email)
        )
        existing_user = result.scalar_one_or_none()
        if existing_user:
            # 🔴 修正: メール確認未完了のユーザーの場合、確認メール再送信を促す
            if not existing_user.email_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "このメールアドレスは既に登録されていますが、メール確認が完了していません。"
                        "確認メールを再送信してください。"
                        "\n\n"
                        "This email address is already registered but not verified. "
                        "Please resend the verification email."
                    )
                )
            else:
                # メール確認済みのユーザーの場合、通常のエラー
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
            language_limit=plan_defaults['language_limit'],
            show_email_on_guest_screen=True
        )
        db.add(facility)
        await db.flush()
        
        # メール確認トークン生成
        verification_token = str(uuid.uuid4())
        verification_token_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        
        # ユーザー作成（is_active=False, メール確認トークン設定）
        user = User(
            facility_id=facility.id,
            email=request.email,
            password_hash=hash_password(request.password),
            role="owner",
            full_name=None,
            is_active=False,  # メール確認まで無効
            email_verified=False,  # メール未確認
            verification_token=verification_token,
            verification_token_expires=verification_token_expires
        )
        db.add(user)
        await db.flush()
        
        # コミット（施設・ユーザー作成を確定）
        await db.commit()
        
        return user, facility

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
    async def register_facility_async_stripe(facility_id: int, plan_type: str) -> None:
        """
        新規登録後、有料プランの場合に Stripe Customer および Subscription を作成し DB を更新する（Phase F #2）。
        別トランザクションで実行。失敗時はログのみ残し施設はそのまま（後でプラン変更 API で補完可能）。
        """
        from app.database import AsyncSessionLocal

        if plan_type == "Free":
            return
        if not stripe_service.is_stripe_configured():
            logger.debug(
                "Stripe not configured, skipping Stripe Customer/Subscription creation for facility_id=%s",
                facility_id,
            )
            return
        async with AsyncSessionLocal() as db:
            try:
                result = await db.execute(select(Facility).where(Facility.id == facility_id))
                facility = result.scalar_one_or_none()
                if not facility:
                    logger.warning("Facility not found for Stripe creation: facility_id=%s", facility_id)
                    return
                # 既に Stripe 連携済みならスキップ（二重作成防止）
                if facility.stripe_customer_id:
                    logger.debug("Facility already has stripe_customer_id, skipping: facility_id=%s", facility_id)
                    return
                # Stripe Customer 作成
                customer = stripe_service.create_customer(
                    email=facility.email,
                    name=facility.name,
                    facility_id=facility.id,
                )
                facility.stripe_customer_id = customer.id
                await db.flush()
                # 有料プラン用 Price ID 取得
                price_id = stripe_service.get_price_id_for_plan(plan_type)
                if not price_id:
                    logger.warning(
                        "No Stripe Price ID for plan_type=%s, facility_id=%s; Customer created only",
                        plan_type,
                        facility_id,
                    )
                    await db.commit()
                    return
                # Subscription 作成
                sub = stripe_service.create_subscription(
                    customer_id=facility.stripe_customer_id,
                    price_id=price_id,
                    facility_id=facility.id,
                )
                facility.stripe_subscription_id = sub.id
                facility.subscription_status = sub.get("status") or "active"
                facility.plan_updated_at = datetime.now(timezone.utc)
                await db.commit()
                logger.info(
                    "Stripe Customer and Subscription created for facility_id=%s, plan_type=%s",
                    facility_id,
                    plan_type,
                )
            except Exception as e:
                logger.warning(
                    "Stripe Customer/Subscription creation failed for facility_id=%s, plan_type=%s: %s. "
                    "Facility remains without Stripe; use plan change API to retry.",
                    facility_id,
                    plan_type,
                    str(e),
                    exc_info=True,
                )
                # 施設は stripe_customer_id 等 NULL のまま。プラン変更 API で後から作成可能。

    @staticmethod
    async def verify_email(
        db: AsyncSession,
        request: VerifyEmailRequest
    ) -> VerifyEmailResponse:
        """
        メールアドレス確認処理（🟠 セキュリティ強化）
        
        Args:
            db: データベースセッション
            request: メールアドレス確認リクエスト
        
        Returns:
            メールアドレス確認レスポンス
        
        Raises:
            HTTPException: 確認失敗時
        """
        # トークンでユーザー取得
        result = await db.execute(
            select(User).where(User.verification_token == request.token)
        )
        user = result.scalar_one_or_none()
        
        # 🟠 トークンが存在しない、または有効期限切れの場合は同じエラーメッセージ
        # （セキュリティ: トークンの存在・非存在を推測させない）
        if user is None:
            # 🔴 修正: トークンがNULL（既に使用済み）の場合、エラーメッセージを改善
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid or expired verification token. "
                    "This token may have already been used. "
                    "If you have already verified your email, please try logging in. "
                    "Otherwise, please request a new verification email."
                )
            )
        
        # トークンが存在するが、有効期限切れの場合
        if user.verification_token_expires and \
           user.verification_token_expires < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token. Please request a new one."
            )
        
        # 既に確認済みの場合
        if user.email_verified:
            # 🔴 修正: エラーではなく、成功レスポンスを返す
            return VerifyEmailResponse(
                message="Email already verified. You can log in now.",
                email=user.email
            )
        
        # メールアドレス確認完了
        user.email_verified = True
        user.is_active = True  # アカウント有効化
        user.verification_token = None  # トークンクリア
        user.verification_token_expires = None  # 有効期限クリア
        
        await db.commit()
        await db.refresh(user)
        
        logger.info(
            f"Email verified successfully: user_id={user.id}, email={user.email}"
        )
        
        return VerifyEmailResponse(
            message="Email verified successfully. You can now log in.",
            email=user.email
        )
    
    @staticmethod
    async def resend_verification_email(
        db: AsyncSession,
        request: ResendVerificationRequest
    ) -> ResendVerificationResponse:
        """
        確認メール再送信処理
        
        Args:
            db: データベースセッション
            request: 確認メール再送信リクエスト
        
        Returns:
            確認メール再送信レスポンス
        
        Raises:
            HTTPException: 再送信失敗時
        """
        # メールアドレスでユーザー取得
        result = await db.execute(
            select(User).where(User.email == request.email)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            # セキュリティ上、ユーザーが存在しない場合でも同じレスポンスを返す
            return ResendVerificationResponse(
                message="If the email address is registered, a verification email has been sent.",
                email=request.email
            )
        
        # 既に確認済みの場合
        if user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        # 新しいトークン生成
        user.verification_token = str(uuid.uuid4())
        user.verification_token_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        
        await db.commit()
        await db.refresh(user)
        
        # 施設情報取得
        facility_result = await db.execute(
            select(Facility).where(Facility.id == user.facility_id)
        )
        facility = facility_result.scalar_one_or_none()
        
        # メール確認URL生成
        verification_url = (
            f"{settings.frontend_url}/admin/verify-email"
            f"?token={user.verification_token}"
        )
        
        # メール送信
        email_service = EmailService()
        email_sent = False
        error_message = None
        
        try:
            email_sent = await email_service.send_verification_reminder_email(
                to_email=user.email,
                to_name=facility.name if facility else "User",
                verification_url=verification_url
            )
        except Exception as e:
            error_message = str(e)
            logger.error(
                f"Failed to resend verification email: user_id={user.id}, "
                f"email={user.email}, error={error_message}"
            )
        
        # 🟠 メール送信失敗時の管理者通知
        if not email_sent:
            try:
                await notify_admin_email_failure(
                    user_email=user.email,
                    facility_name=facility.name if facility else "Unknown",
                    error_message=error_message or "Unknown error"
                )
            except Exception as notify_error:
                logger.error(
                    f"Failed to notify admin: {str(notify_error)}",
                    exc_info=True
                )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email. Please try again later."
            )
        
        logger.info(
            f"Verification email resent: user_id={user.id}, email={user.email}"
        )
        
        return ResendVerificationResponse(
            message="Verification email resent successfully. Please check your inbox.",
            email=user.email
        )

    @staticmethod
    async def request_password_reset(db: AsyncSession, email: str) -> PasswordResetResponse:
        """
        パスワードリセット依頼処理。
        ユーザーが存在しない場合も同じ成功メッセージを返す（情報漏れ防止）。
        """
        result = await db.execute(
            select(User).where(User.email == email, User.is_active == True)
        )
        user = result.scalar_one_or_none()

        if user is None:
            logger.info(f"Password reset requested for unknown email: {email}")
            return PasswordResetResponse(
                message="If an account exists for this email, you will receive a password reset link."
            )

        token = str(uuid.uuid4())
        expires = datetime.now(timezone.utc) + timedelta(hours=1)
        user.password_reset_token = token
        user.password_reset_expires = expires
        await db.commit()
        await db.refresh(user)

        reset_url = f"{settings.frontend_url}/admin/password-reset/confirm?token={token}"
        to_name = user.full_name or user.email

        try:
            if settings.brevo_api_key:
                email_service = EmailService()
                await email_service.send_password_reset_email(
                    to_email=user.email,
                    to_name=to_name,
                    reset_url=reset_url
                )
                logger.info(f"Password reset email sent: user_id={user.id}, email={user.email}")
            else:
                logger.warning(
                    "BREVO_API_KEY not set; password reset email not sent. "
                    f"user_id={user.id}, reset_url={reset_url}"
                )
        except Exception as e:
            logger.error(
                f"Failed to send password reset email: user_id={user.id}, "
                f"email={user.email}, error={str(e)}",
                exc_info=True
            )

        return PasswordResetResponse(
            message="If an account exists for this email, you will receive a password reset link."
        )

    @staticmethod
    async def confirm_password_reset(
        db: AsyncSession,
        token: str,
        new_password: str,
        confirm_password: str
    ) -> PasswordResetResponse:
        """
        パスワードリセット確定処理。
        トークン検証後、パスワードを更新しトークンを無効化する。
        """
        if new_password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password and confirm password do not match"
            )
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )

        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(User).where(
                User.password_reset_token == token,
                User.password_reset_expires > now
            )
        )
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )

        user.password_hash = hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        await db.commit()

        logger.info(f"Password reset completed: user_id={user.id}, email={user.email}")

        return PasswordResetResponse(
            message="Password has been reset successfully."
        )

    @staticmethod
    async def register_facility(
        db: AsyncSession,
        request: FacilityRegisterRequest,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> FacilityRegisterResponse:
        """
        施設登録処理（メール確認メール送信）
        
        Args:
            db: データベースセッション
            request: 施設登録リクエスト
            background_tasks: バックグラウンドタスク（オプション）
        
        Returns:
            施設登録レスポンス（メール確認待ち）
        
        Raises:
            HTTPException: 登録失敗時
        """
        # 施設・ユーザー作成（同期処理）
        user, facility = await AuthService.register_facility_sync(db, request)

        # 有料プラン時は Stripe Customer / Subscription を別トランザクションで作成（Phase F #2）
        if facility.plan_type != "Free":
            if background_tasks:
                background_tasks.add_task(
                    AuthService.register_facility_async_stripe,
                    facility.id,
                    facility.plan_type,
                )
            else:
                await AuthService.register_facility_async_stripe(facility.id, facility.plan_type)

        # メール確認URL生成
        verification_url = (
            f"{settings.frontend_url}/admin/verify-email"
            f"?token={user.verification_token}"
        )
        
        # 🔴 メール送信（リトライ処理付き）
        email_service = None
        email_sent = False
        error_message = None
        
        try:
            # 🔴 環境変数チェック
            if not settings.brevo_api_key:
                raise ValueError(
                    "BREVO_API_KEY is not set. Please configure Brevo API Key in your .env file. "
                    "See: https://app.brevo.com/settings/keys/api"
                )
            
            email_service = EmailService()
            email_sent = await email_service.send_verification_email(
                to_email=user.email,
                to_name=facility.name,
                verification_url=verification_url
            )
        except ValueError as e:
            # 🔴 環境変数未設定エラー（明確なエラーメッセージ）
            error_message = str(e)
            logger.error(
                f"Email service configuration error: user_id={user.id}, "
                f"email={user.email}, error={error_message}"
            )
            # 管理者に通知（Brevo API Keyが設定されていない場合でも通知を試みる）
            if settings.admin_notification_email:
                try:
                    await notify_admin_email_failure(
                        user_email=user.email,
                        facility_name=facility.name,
                        error_message=error_message
                    )
                except Exception as notify_error:
                    logger.error(
                        f"Failed to send admin notification: {str(notify_error)}",
                        exc_info=True
                    )
        except Exception as e:
            error_message = str(e)
            logger.error(
                f"Failed to send verification email after retries: "
                f"user_id={user.id}, email={user.email}, error={error_message}",
                exc_info=True
            )
            # 管理者に通知
            if settings.admin_notification_email:
                try:
                    await notify_admin_email_failure(
                        user_email=user.email,
                        facility_name=facility.name,
                        error_message=error_message
                    )
                except Exception as notify_error:
                    logger.error(
                        f"Failed to send admin notification: {str(notify_error)}",
                        exc_info=True
                    )
        
        # 🔴 メール送信失敗時のログ強化
        if not email_sent:
            logger.error(
                f"❌ Email verification was NOT sent: user_id={user.id}, "
                f"email={user.email}, error={error_message or 'Unknown error'}"
            )
        
        # 🔴 FAQ自動投入をバックグラウンドで実行（メール送信状況に関係なく実行）
        if background_tasks:
            background_tasks.add_task(
                AuthService.register_facility_async_faqs,
                facility.id,
                user.id,
                request.subscription_plan
            )
        else:
            logger.warning(
                "BackgroundTasks not available, running FAQ creation synchronously"
            )
            await AuthService.register_facility_async_faqs(
                facility.id,
                user.id,
                request.subscription_plan
            )
        
        # 🔴 修正: メール送信失敗時は警告メッセージを返す
        if not email_sent:
            return FacilityRegisterResponse(
                message=(
                    "登録は完了しましたが、確認メールの送信に失敗しました。"
                    "確認メール再送信機能をご利用ください。"
                    "\n\n"
                    "Registration completed, but verification email sending failed. "
                    "Please use the resend verification email function."
                ),
                email=user.email,
                facility_name=facility.name
            )
        
        return FacilityRegisterResponse(
            message=(
                "Registration successful. Please check your email to verify your account."
            ),
            email=user.email,
            facility_name=facility.name
        )

