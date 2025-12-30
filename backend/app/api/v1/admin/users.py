"""
ユーザー管理APIエンドポイント
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.facility import Facility
from app.models.faq import FAQ
from app.schemas.user import UserResponse

router = APIRouter(prefix="/admin/users", tags=["admin", "users"])


@router.get("", response_model=List[UserResponse])
async def get_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ユーザー一覧取得
    
    現在のユーザーが所属する施設のユーザー一覧を返却します。
    """
    try:
        # 現在のユーザーが管理者権限を持っているかチェック（ownerロールのみ）
        if current_user.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only facility owners can view users"
            )
        
        # 同じ施設のユーザーを取得
        result = await db.execute(
            select(User).where(User.facility_id == current_user.facility_id)
        )
        users = result.scalars().all()
        
        return users
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ユーザー削除
    
    指定されたユーザーを削除します。関連する施設とFAQも削除されます。
    """
    try:
        # 現在のユーザーが管理者権限を持っているかチェック（ownerロールのみ）
        if current_user.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only facility owners can delete users"
            )
        
        # 削除対象ユーザーを取得
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user_to_delete = result.scalar_one_or_none()
        
        if not user_to_delete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 同じ施設のユーザーのみ削除可能
        if user_to_delete.facility_id != current_user.facility_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete users from other facilities"
            )
        
        # 自分自身は削除不可
        if user_to_delete.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete yourself"
            )
        
        # バックアップ情報ログ出力
        print(f"[BACKUP] Deleting user: {user_to_delete.email}, facility_id: {user_to_delete.facility_id}")
        
        # 関連するFAQを削除
        await db.execute(
            delete(FAQ).where(FAQ.facility_id == user_to_delete.facility_id)
        )
        
        # 施設を削除
        await db.execute(
            delete(Facility).where(Facility.id == user_to_delete.facility_id)
        )
        
        # ユーザーを削除
        await db.execute(
            delete(User).where(User.id == user_id)
        )
        
        await db.commit()
        
        return {"message": f"User {user_to_delete.email} and related data deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )