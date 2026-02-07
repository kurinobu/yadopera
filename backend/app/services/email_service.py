"""
メール送信サービス（Brevo連携）
"""

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from app.core.config import settings
import logging
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential  # 🟡 リトライ

logger = logging.getLogger(__name__)


class EmailService:
    """
    Brevoを使用したメール送信サービス
    """
    
    def __init__(self):
        """
        Brevo API設定
        """
        # 🔴 環境変数の検証
        if not settings.brevo_api_key:
            raise ValueError(
                "BREVO_API_KEY is not set. Please set BREVO_API_KEY in your .env file. "
                "Email sending is disabled."
            )
        
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.brevo_api_key
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
    
    # 🟡 リトライ処理追加（中優先）
    # 最大3回リトライ、待機時間: 2秒、4秒、8秒（指数バックオフ）
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def send_verification_email(
        self,
        to_email: str,
        to_name: str,
        verification_url: str
    ) -> bool:
        """
        メールアドレス確認メールを送信（リトライあり）
        
        Args:
            to_email: 送信先メールアドレス
            to_name: 送信先名（施設名）
            verification_url: 確認用URL
        
        Returns:
            送信成功時True、失敗時False
        """
        try:
            # メール本文（HTML）
            html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>メールアドレス確認 - YadOPERA</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; border-radius: 10px; padding: 30px; margin-bottom: 20px;">
        <h1 style="color: #2563eb; margin-top: 0;">YadOPERA</h1>
        <h2 style="color: #1f2937; margin-bottom: 20px;">メールアドレス確認</h2>
        
        <p style="font-size: 16px; margin-bottom: 20px;">
            {to_name} 様
        </p>
        
        <p style="font-size: 16px; margin-bottom: 20px;">
            YadOPERAにご登録いただきありがとうございます。<br>
            以下のボタンをクリックして、メールアドレスの確認を完了してください。
        </p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}" 
               style="display: inline-block; background-color: #2563eb; color: white; 
                      padding: 15px 40px; text-decoration: none; border-radius: 5px; 
                      font-size: 16px; font-weight: bold;">
                メールアドレスを確認する
            </a>
        </div>
        
        <p style="font-size: 14px; color: #6b7280; margin-bottom: 10px;">
            ボタンをクリックできない場合は、以下のURLをブラウザにコピー＆ペーストしてください：
        </p>
        <p style="font-size: 14px; color: #2563eb; word-break: break-all; margin-bottom: 20px;">
            {verification_url}
        </p>
        
        <p style="font-size: 14px; color: #ef4444; margin-bottom: 10px;">
            <strong>※ このリンクは24時間後に無効になります。</strong>
        </p>
        
        <p style="font-size: 14px; color: #6b7280; margin-bottom: 20px;">
            このメールに心当たりがない場合は、無視していただいて構いません。
        </p>
    </div>
    
    <div style="text-align: center; font-size: 12px; color: #9ca3af; padding-top: 20px; border-top: 1px solid #e5e7eb;">
        <p>© 2026 YadOPERA. All rights reserved.</p>
        <p>このメールは送信専用です。返信いただいてもお答えできません。</p>
    </div>
</body>
</html>
            """
            
            # メール本文（プレーンテキスト）
            text_content = f"""
YadOPERA - メールアドレス確認

{to_name} 様

YadOPERAにご登録いただきありがとうございます。
以下のURLにアクセスして、メールアドレスの確認を完了してください。

{verification_url}

※ このリンクは24時間後に無効になります。

このメールに心当たりがない場合は、無視していただいて構いません。

---
© 2026 YadOPERA. All rights reserved.
このメールは送信専用です。返信いただいてもお答えできません。
            """
            
            # メール送信設定
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email, "name": to_name}],
                sender={
                    "email": settings.brevo_sender_email,
                    "name": settings.brevo_sender_name
                },
                subject="【YadOPERA】メールアドレス確認のお願い",
                html_content=html_content,
                text_content=text_content
            )
            
            # メール送信
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(
                f"Verification email sent successfully: to={to_email}, "
                f"message_id={api_response.message_id}"
            )
            return True
            
        except ApiException as e:
            logger.error(
                f"Brevo API error: to={to_email}, status={e.status}, "
                f"reason={e.reason}, body={e.body}"
            )
            raise  # 🟡 tenacityがリトライする
        except Exception as e:
            logger.error(
                f"Unexpected error sending verification email: to={to_email}, "
                f"error={str(e)}",
                exc_info=True
            )
            raise  # 🟡 tenacityがリトライする
    
    # 🟡 リトライ処理追加（中優先）
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def send_verification_reminder_email(
        self,
        to_email: str,
        to_name: str,
        verification_url: str
    ) -> bool:
        """
        メールアドレス確認リマインダーメールを送信（再送信用、リトライあり）
        
        Args:
            to_email: 送信先メールアドレス
            to_name: 送信先名（施設名）
            verification_url: 確認用URL
        
        Returns:
            送信成功時True、失敗時False
        """
        try:
            # メール本文（HTML）
            html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>メールアドレス確認（再送） - YadOPERA</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; border-radius: 10px; padding: 30px; margin-bottom: 20px;">
        <h1 style="color: #2563eb; margin-top: 0;">YadOPERA</h1>
        <h2 style="color: #1f2937; margin-bottom: 20px;">メールアドレス確認（再送）</h2>
        
        <p style="font-size: 16px; margin-bottom: 20px;">
            {to_name} 様
        </p>
        
        <p style="font-size: 16px; margin-bottom: 20px;">
            メールアドレス確認メールを再送信いたしました。<br>
            以下のボタンをクリックして、メールアドレスの確認を完了してください。
        </p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}" 
               style="display: inline-block; background-color: #2563eb; color: white; 
                      padding: 15px 40px; text-decoration: none; border-radius: 5px; 
                      font-size: 16px; font-weight: bold;">
                メールアドレスを確認する
            </a>
        </div>
        
        <p style="font-size: 14px; color: #6b7280; margin-bottom: 10px;">
            ボタンをクリックできない場合は、以下のURLをブラウザにコピー＆ペーストしてください：
        </p>
        <p style="font-size: 14px; color: #2563eb; word-break: break-all; margin-bottom: 20px;">
            {verification_url}
        </p>
        
        <p style="font-size: 14px; color: #ef4444; margin-bottom: 10px;">
            <strong>※ このリンクは24時間後に無効になります。</strong>
        </p>
        
        <p style="font-size: 14px; color: #6b7280; margin-bottom: 20px;">
            このメールに心当たりがない場合は、無視していただいて構いません。
        </p>
    </div>
    
    <div style="text-align: center; font-size: 12px; color: #9ca3af; padding-top: 20px; border-top: 1px solid #e5e7eb;">
        <p>© 2026 YadOPERA. All rights reserved.</p>
        <p>このメールは送信専用です。返信いただいてもお答えできません。</p>
    </div>
</body>
</html>
            """
            
            # メール本文（プレーンテキスト）
            text_content = f"""
YadOPERA - メールアドレス確認（再送）

{to_name} 様

メールアドレス確認メールを再送信いたしました。
以下のURLにアクセスして、メールアドレスの確認を完了してください。

{verification_url}

※ このリンクは24時間後に無効になります。

このメールに心当たりがない場合は、無視していただいて構いません。

---
© 2026 YadOPERA. All rights reserved.
このメールは送信専用です。返信いただいてもお答えできません。
            """
            
            # メール送信設定
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email, "name": to_name}],
                sender={
                    "email": settings.brevo_sender_email,
                    "name": settings.brevo_sender_name
                },
                subject="【YadOPERA】メールアドレス確認のお願い（再送）",
                html_content=html_content,
                text_content=text_content
            )
            
            # メール送信
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(
                f"Verification reminder email sent successfully: to={to_email}, "
                f"message_id={api_response.message_id}"
            )
            return True
            
        except ApiException as e:
            logger.error(
                f"Brevo API error (reminder): to={to_email}, status={e.status}, "
                f"reason={e.reason}, body={e.body}"
            )
            raise  # 🟡 tenacityがリトライする
        except Exception as e:
            logger.error(
                f"Unexpected error sending verification reminder email: to={to_email}, "
                f"error={str(e)}",
                exc_info=True
            )
            raise  # 🟡 tenacityがリトライする

