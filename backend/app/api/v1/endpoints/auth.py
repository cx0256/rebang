from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.database import get_db

router = APIRouter()


@router.post("/login")
async def login(
    credentials: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    # 简单的登录实现
    username = credentials.get("username")
    password = credentials.get("password")
    
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )
    
    # 这里应该验证用户凭据
    # 暂时返回成功响应
    return {
        "success": True,
        "data": {
            "access_token": "fake-token",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "username": username
            }
        }
    }


@router.post("/logout")
async def logout():
    """用户登出"""
    return {"success": True, "message": "Logged out successfully"}


@router.get("/me")
async def get_current_user():
    """获取当前用户信息"""
    return {
        "success": True,
        "data": {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com"
        }
    }