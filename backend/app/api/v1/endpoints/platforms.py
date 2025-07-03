from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.hot_list_service import HotListService

router = APIRouter()


@router.get("/")
async def get_platforms(
    db: AsyncSession = Depends(get_db)
):
    """获取所有平台列表"""
    service = HotListService(db)
    try:
        platforms = await service.get_all_platforms()
        return {"success": True, "data": platforms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{platform_id}")
async def get_platform(
    platform_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个平台信息"""
    service = HotListService(db)
    try:
        platform = await service.get_platform_by_id(platform_id)
        if not platform:
            raise HTTPException(status_code=404, detail="Platform not found")
        return {"success": True, "data": platform}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))