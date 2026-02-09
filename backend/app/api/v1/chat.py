"""
チャットAPIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas.chat import (
    ChatRequest, ChatResponse, ChatHistoryResponse, 
    FeedbackRequest, FeedbackResponse,
    EscalationRequest, EscalationResponse
)
from app.services.chat_service import ChatService
from app.services.escalation_service import EscalationService
from app.models.conversation import Conversation
from typing import Optional

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    チャットメッセージ送信（RAG統合型）
    
    - **facility_id**: 施設ID
    - **message**: メッセージ内容（1-1000文字）
    - **language**: 言語コード（デフォルト: "en"）
    - **location**: QRコード設置場所（オプション）
    - **session_id**: 既存セッションID（オプション、指定時は既存会話に追加）
    
    RAG統合型でAI応答を生成し、エスカレーション判定を行います。
    スタッフ不在時間帯の場合はスタッフ不在時間帯対応キューに追加されます。
    """
    try:
        # エラーログで施設紐づけするため state に保持
        http_request.state.facility_id = request.facility_id
        # リクエストヘッダーから情報を取得
        user_agent = http_request.headers.get("user-agent")
        ip_address = http_request.client.host if http_request.client else None
        
        # ChatServiceでメッセージ処理
        chat_service = ChatService(db)
        response = await chat_service.process_chat_message(
            request=request,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        return response
    
    except ValueError as e:
        # バリデーションエラー
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    facility_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    会話履歴取得
    
    - **session_id**: セッションID（必須）
    - **facility_id**: 施設ID（オプション、指定時はその施設の会話のみ）
    
    指定されたセッションIDの会話履歴を時系列順に返却します。
    """
    try:
        chat_service = ChatService(db)
        history = await chat_service.get_conversation_history(
            session_id=session_id,
            facility_id=facility_id
        )
        
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation not found: session_id={session_id}"
            )
        
        return history
    
    except HTTPException:
        raise
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chat history: {str(e)}"
        )


@router.post("/feedback", response_model=FeedbackResponse)
async def send_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    ゲストフィードバック送信（v0.3新規）
    
    - **message_id**: メッセージID（必須）
    - **feedback_type**: フィードバックタイプ（positive/negative、必須）
    
    ゲストからのフィードバック（👍👎）を保存します。
    低評価回答（negative）が2回以上ついた場合は自動ハイライトされます。
    """
    try:
        chat_service = ChatService(db)
        feedback = await chat_service.save_feedback(
            message_id=request.message_id,
            feedback_type=request.feedback_type
        )
        
        return feedback
    
    except ValueError as e:
        # バリデーションエラー
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving feedback: {str(e)}"
        )


@router.post("/escalate", response_model=EscalationResponse)
async def escalate_to_staff(
    request: EscalationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    スタッフへのエスカレーション（ゲスト側、v0.3新規）
    
    - **facility_id**: 施設ID（必須）
    - **session_id**: セッションID（必須）
    
    ゲストが「スタッフに連絡」ボタンをタップした際に呼び出されます。
    エスカレーションを作成し、管理画面の未解決質問リストに表示されます。
    """
    try:
        # セッション有効期限をチェック（防止策1: started_atベースの固定有効期限）
        from app.utils.session import is_session_valid
        is_valid = await is_session_valid(request.session_id, db)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Session expired: session_id={request.session_id}"
            )
        
        # セッションIDから会話を取得
        result = await db.execute(
            select(Conversation).where(
                Conversation.facility_id == request.facility_id,
                Conversation.session_id == request.session_id
            )
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation not found: session_id={request.session_id}, facility_id={request.facility_id}"
            )
        
        # エスカレーションサービスでエスカレーションを作成
        escalation_service = EscalationService()
        escalation = await escalation_service.create_escalation(
            facility_id=request.facility_id,
            conversation_id=conversation.id,
            trigger_type="staff_mode",  # 手動エスカレーション
            ai_confidence=0.0,  # 手動エスカレーションのため信頼度は0.0
            escalation_mode="normal",
            notification_channels=["email"],
            db=db
        )
        
        return EscalationResponse(
            success=True,
            escalation_id=escalation.id,
            message="エスカレーションが作成されました。スタッフが対応いたします。"
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        # バリデーションエラー
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating escalation: {str(e)}"
        )

