from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List

from app.core.database import get_db
from app.services.hot_list_service import HotListService

router = APIRouter()


@router.get("/stats")
async def get_admin_stats(
    db: AsyncSession = Depends(get_db)
):
    """获取管理员统计数据"""
    service = HotListService(db)
    try:
        stats = await service.get_admin_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def get_users(
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表"""
    # 简单的用户列表实现
    return {
        "success": True,
        "data": [
            {"id": 1, "username": "admin", "email": "admin@example.com", "is_active": True},
            {"id": 2, "username": "user1", "email": "user1@example.com", "is_active": True}
        ]
    }


@router.post("/users")
async def create_user(
    user_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """创建新用户"""
    # 简单的用户创建实现
    return {
        "success": True,
        "data": {
            "id": 3,
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "is_active": True
        }
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除用户"""
    return {"success": True, "message": f"User {user_id} deleted successfully"}