from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.hot_list_service import HotListService

router = APIRouter()


@router.get("/")
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    """获取所有分类列表"""
    service = HotListService(db)
    try:
        categories = await service.get_all_categories()
        return {"success": True, "data": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{category_id}")
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个分类信息"""
    service = HotListService(db)
    try:
        category = await service.get_category_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return {"success": True, "data": category}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))