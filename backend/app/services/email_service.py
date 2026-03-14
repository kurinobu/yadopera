"""
メール送信サービス（Brevo連携）
"""

import base64
import logging
from typing import Optional

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from tenacity import retry, stop_after_attempt, wait_exponential  # 🟡 リトライ

from app.core.config import settings

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

    # 🟡 リトライ処理追加（パスワードリセット用）
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def send_password_reset_email(
        self,
        to_email: str,
        to_name: str,
        reset_url: str
    ) -> bool:
        """
        パスワードリセット用メールを送信（リトライあり）

        Args:
            to_email: 送信先メールアドレス
            to_name: 送信先名（施設名またはユーザー名）
            reset_url: パスワードリセット確認用URL（1時間有効）

        Returns:
            送信成功時True
        """
        try:
            html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>パスワードリセット - YadOPERA</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; border-radius: 10px; padding: 30px; margin-bottom: 20px;">
        <h1 style="color: #2563eb; margin-top: 0;">YadOPERA</h1>
        <h2 style="color: #1f2937; margin-bottom: 20px;">パスワードリセットのご案内</h2>

        <p style="font-size: 16px; margin-bottom: 20px;">
            {to_name} 様
        </p>

        <p style="font-size: 16px; margin-bottom: 20px;">
            パスワードリセットのリクエストを受け付けました。<br>
            以下のボタンをクリックして、新しいパスワードを設定してください。
        </p>

        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}"
               style="display: inline-block; background-color: #2563eb; color: white;
                      padding: 15px 40px; text-decoration: none; border-radius: 5px;
                      font-size: 16px; font-weight: bold;">
                パスワードを再設定する
            </a>
        </div>

        <p style="font-size: 14px; color: #6b7280; margin-bottom: 10px;">
            ボタンをクリックできない場合は、以下のURLをブラウザにコピー＆ペーストしてください：
        </p>
        <p style="font-size: 14px; color: #2563eb; word-break: break-all; margin-bottom: 20px;">
            {reset_url}
        </p>

        <p style="font-size: 14px; color: #ef4444; margin-bottom: 10px;">
            <strong>※ このリンクは1時間後に無効になります。</strong>
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

            text_content = f"""
YadOPERA - パスワードリセットのご案内

{to_name} 様

パスワードリセットのリクエストを受け付けました。
以下のURLにアクセスして、新しいパスワードを設定してください。

{reset_url}

※ このリンクは1時間後に無効になります。

このメールに心当たりがない場合は、無視していただいて構いません。

---
© 2026 YadOPERA. All rights reserved.
このメールは送信専用です。返信いただいてもお答えできません。
            """

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email, "name": to_name}],
                sender={
                    "email": settings.brevo_sender_email,
                    "name": settings.brevo_sender_name
                },
                subject="【YadOPERA】パスワードリセットのご案内",
                html_content=html_content,
                text_content=text_content
            )

            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(
                f"Password reset email sent successfully: to={to_email}, "
                f"message_id={api_response.message_id}"
            )
            return True

        except ApiException as e:
            logger.error(
                f"Brevo API error (password reset): to={to_email}, status={e.status}, "
                f"reason={e.reason}, body={e.body}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error sending password reset email: to={to_email}, "
                f"error={str(e)}",
                exc_info=True
            )
            raise

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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def send_coupon_email(
        self,
        to_email: str,
        to_name: Optional[str],
        facility_name: str,
        discount_percent: int,
        description: Optional[str],
        valid_until: str,
        official_website_url: Optional[str] = None,
    ) -> bool:
        """
        クーポン送付メールを送信（リードゲットオプション）
        
        Args:
            to_email: 送信先メールアドレス
            to_name: 送信先名（ゲスト名、任意）
            facility_name: 施設名
            discount_percent: 割引率（%）
            description: クーポン文言（施設が編集したもの、任意）
            valid_until: 有効期限の表示用文字列（例: 2026年8月21日まで）
            official_website_url: 公式サイトURL（任意。設定時はメール本文に「ご予約はこちら」を追加）
        
        Returns:
            送信成功時True、失敗時False
        """
        display_name = to_name or to_email
        try:
            desc_block = f"<p style=\"font-size: 14px; color: #6b7280; margin-bottom: 20px;\">{description}</p>" if description else ""
            url_block_html = ""
            if official_website_url and official_website_url.strip():
                url_block_html = f"<p style=\"font-size: 14px; margin-bottom: 20px;\">ご予約はこちら: <a href=\"{official_website_url.strip()}\">{official_website_url.strip()}</a></p>"
            html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>クーポンのお届け - YadOPERA</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #f8f9fa; border-radius: 10px; padding: 30px; margin-bottom: 20px;">
        <h1 style="color: #2563eb; margin-top: 0;">YadOPERA</h1>
        <h2 style="color: #1f2937; margin-bottom: 20px;">{facility_name} のクーポン</h2>
        
        <p style="font-size: 16px; margin-bottom: 20px;">
            {display_name} 様
        </p>
        
        <p style="font-size: 16px; margin-bottom: 20px;">
            このたびはクーポンをご利用いただきありがとうございます。<br>
            <strong>次回、{facility_name} の公式サイトからご予約いただくと {discount_percent}% OFF</strong> になります。
        </p>
        {desc_block}
        <p style="font-size: 14px; color: #6b7280; margin-bottom: 10px;">
            <strong>有効期限:</strong> {valid_until}
        </p>
        {url_block_html}
        <p style="font-size: 14px; color: #6b7280; margin-bottom: 20px;">
            ご利用の際は、チェックイン時やお支払い時にこのクーポンをご提示ください。
        </p>
    </div>
    
    <div style="text-align: center; font-size: 12px; color: #9ca3af; padding-top: 20px; border-top: 1px solid #e5e7eb;">
        <p>© 2026 YadOPERA. All rights reserved.</p>
        <p>このメールは送信専用です。返信いただいてもお答えできません。</p>
    </div>
</body>
</html>
            """
            url_block_text = ""
            if official_website_url and official_website_url.strip():
                url_block_text = f"\nご予約はこちら: {official_website_url.strip()}\n"
            text_content = f"""
YadOPERA - {facility_name} のクーポン

{display_name} 様

このたびはクーポンをご利用いただきありがとうございます。
次回、{facility_name} の公式サイトからご予約いただくと {discount_percent}% OFF になります。

有効期限: {valid_until}
{url_block_text}
ご利用の際は、チェックイン時やお支払い時にこのクーポンをご提示ください。

---
© 2026 YadOPERA. All rights reserved.
このメールは送信専用です。返信いただいてもお答えできません。
            """
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": to_email, "name": display_name}],
                sender={
                    "email": settings.brevo_sender_email,
                    "name": settings.brevo_sender_name
                },
                subject=f"【YadOPERA】{facility_name} の {discount_percent}% OFF クーポン",
                html_content=html_content,
                text_content=text_content
            )
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            logger.info(
                f"Coupon email sent successfully: to={to_email}, facility={facility_name}, "
                f"message_id={api_response.message_id}"
            )
            return True
        except ApiException as e:
            logger.error(
                f"Brevo API error (coupon): to={to_email}, status={e.status}, "
                f"reason={e.reason}, body={e.body}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error sending coupon email: to={to_email}, error={str(e)}",
                exc_info=True
            )
            raise

    async def send_csv_bulk_request_email(
        self,
        form_data: dict,
        file_bytes: Optional[bytes] = None,
        filename: Optional[str] = None,
    ) -> bool:
        """
        CSV一括登録代行の申し込み内容を運営あてに送信（添付ファイル対応）。
        呼び出し元で admin_notification_email 未設定時は 503 を返す想定。
        """
        if not settings.admin_notification_email:
            raise ValueError("ADMIN_NOTIFICATION_EMAIL is not set. CSV bulk request cannot be sent.")

        rows = [
            ("施設名", form_data.get("csv_facility_name", "")),
            ("プラン", form_data.get("csv_plan", "")),
            ("希望登録件数", form_data.get("csv_desired_count", "")),
            ("希望言語", form_data.get("csv_languages", "")),
            ("連絡メール", form_data.get("csv_email", "")),
            ("担当者名", form_data.get("csv_contact_name", "")),
            ("その他要望", form_data.get("csv_notes", "")),
        ]
        table_rows = "".join(
            f"<tr><td style=\"padding:4px 8px;border:1px solid #ddd;\">{k}</td><td style=\"padding:4px 8px;border:1px solid #ddd;\">{v}</td></tr>"
            for k, v in rows
        )
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head><meta charset="UTF-8"><title>CSV一括登録代行 申し込み</title></head>
<body style="font-family: sans-serif;">
<h2>【YadOPERA】CSV一括登録代行の申し込み</h2>
<p>管理画面の申し込みフォームから以下の内容が送信されました。</p>
<table style="border-collapse: collapse;">
{table_rows}
</table>
<p style="margin-top: 20px; font-size: 12px; color: #666;">このメールは送信専用です。</p>
</body>
</html>
"""

        send_params = {
            "to": [{"email": settings.admin_notification_email, "name": "YadOPERA Admin"}],
            "sender": {
                "email": settings.brevo_sender_email,
                "name": settings.brevo_sender_name,
            },
            "subject": "【YadOPERA】CSV一括登録代行の申し込み",
            "html_content": html_content,
        }
        if file_bytes and filename:
            send_params["attachment"] = [
                {"name": filename, "content": base64.b64encode(file_bytes).decode()}
            ]

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(**send_params)
        api_response = self.api_instance.send_transac_email(send_smtp_email)
        logger.info(
            f"CSV bulk request email sent: message_id={api_response.message_id}, "
            f"attachment={bool(file_bytes)}"
        )
        return True

