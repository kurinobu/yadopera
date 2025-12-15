"""
ダッシュボードAPIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/admin/dashboard", tags=["admin", "dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ダッシュボードデータ取得
    
    - **週次サマリー**: 過去7日間の統計情報
    - **リアルタイムチャット履歴**: 最新10件の会話
    - **スタッフ不在時間帯対応キュー**: 未解決のスタッフ不在時間帯対応キュー
    - **フィードバック統計**: ゲストフィードバック統計
    
    JWT認証必須。現在のユーザーが所属する施設のデータを返却します。
    """
    try:
        # ユーザーが所属する施設IDを取得
        facility_id = current_user.facility_id
        if not facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not associated with any facility"
            )
        
        # ダッシュボードサービスでデータ取得
        dashboard_service = DashboardService(db)
        dashboard_data = await dashboard_service.get_dashboard_data(facility_id)
        
        # 管理画面向けAPIは常に最新を返すためキャッシュ禁止
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        
        return dashboard_data
    
    except HTTPException:
        raise
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dashboard data: {str(e)}"
        )

