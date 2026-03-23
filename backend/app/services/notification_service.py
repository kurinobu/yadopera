"""
管理者通知サービス
"""

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


async def notify_admin_email_failure(
    user_email: str,
    facility_name: str,
    error_message: str
):
    """
    メール送信失敗を管理者に通知
    
    Args:
        user_email: 送信失敗したユーザーのメールアドレス
        facility_name: 施設名
        error_message: エラーメッセージ
    """
    try:
        # Brevo API設定
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.brevo_api_key
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )
        
        # メール本文
        html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>メール送信失敗通知 - YadOPERA</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="background-color: #fee; border-left: 4px solid #c00; padding: 20px; margin-bottom: 20px;">
        <h2 style="color: #c00; margin-top: 0;">【重要】メール送信失敗通知</h2>
        
        <p><strong>施設名:</strong> {facility_name}</p>
        <p><strong>メールアドレス:</strong> {user_email}</p>
        <p><strong>エラー内容:</strong></p>
        <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto;">{error_message}</pre>
        
        <p style="margin-top: 20px; color: #c00;">
            <strong>対応が必要です。ユーザーに直接連絡して確認メールを手動で送信してください。</strong>
        </p>
    </div>
    
    <div style="font-size: 12px; color: #999; border-top: 1px solid #eee; padding-top: 10px;">
        <p>© 2026 YadOPERA. All rights reserved.</p>
    </div>
</body>
</html>
        """
        
        text_content = f"""
【重要】メール送信失敗通知

施設名: {facility_name}
メールアドレス: {user_email}
エラー内容:
{error_message}

対応が必要です。ユーザーに直接連絡して確認メールを手動で送信してください。

---
© 2026 YadOPERA. All rights reserved.
        """
        
        # メール送信設定
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": settings.admin_notification_email, "name": "YadOPERA Admin"}],
            sender={
                "email": settings.brevo_sender_email,
                "name": "YadOPERA System"
            },
            subject="【YadOPERA】メール送信失敗通知",
            html_content=html_content,
            text_content=text_content
        )
        
        # メール送信
        api_response = api_instance.send_transac_email(send_smtp_email)
        logger.info(
            f"Admin notification sent: user_email={user_email}, "
            f"message_id={api_response.message_id}"
        )
    
    except ApiException as e:
        logger.error(
            f"Failed to send admin notification: user_email={user_email}, "
            f"status={e.status}, reason={e.reason}, body={e.body}"
        )
    except Exception as e:
        logger.error(
            f"Unexpected error sending admin notification: user_email={user_email}, "
            f"error={str(e)}",
            exc_info=True
        )

