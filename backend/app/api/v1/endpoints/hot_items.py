from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.services.hot_list_service import HotListService
from app.schemas.hot_item import HotItemResponse, HotItemListResponse
from app.schemas.common import PaginationParams

router = APIRouter()


@router.get("/", response_model=HotItemListResponse)
async def get_hot_items(
    db: AsyncSession = Depends(get_db),
    category_id: Optional[int] = Query(None, description="分类ID"),
    platform_name: Optional[str] = Query(None, description="平台名称"),
    category_name: Optional[str] = Query(None, description="分类名称"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    hours: Optional[int] = Query(None, ge=1, le=168, description="最近N小时内的数据")
):
    """获取热榜条目列表"""
    service = HotListService(db)
    
    # 构建过滤条件
    filters = {}
    if category_id:
        filters['category_id'] = category_id
    if platform_name:
        filters['platform_name'] = platform_name
    if category_name:
        filters['category_name'] = category_name
    if hours:
        filters['crawled_after'] = datetime.utcnow() - timedelta(hours=hours)
    
    # 分页参数
    pagination = PaginationParams(page=page, size=size)
    
    try:
        result = await service.get_hot_items_paginated(filters, pagination)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热榜数据失败: {str(e)}")


@router.get("/{item_id}", response_model=HotItemResponse)
async def get_hot_item(
    item_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取单个热榜条目详情"""
    service = HotListService(db)
    
    try:
        item = await service.get_hot_item_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="热榜条目不存在")
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热榜条目失败: {str(e)}")


@router.get("/trending/today", response_model=List[HotItemResponse])
async def get_trending_today(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200, description="返回数量")
):
    """获取今日热门条目"""
    service = HotListService(db)
    
    try:
        items = await service.get_trending_items(
            hours=24,
            limit=limit
        )
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取今日热门失败: {str(e)}")


@router.get("/trending/week", response_model=List[HotItemResponse])
async def get_trending_week(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200, description="返回数量")
):
    """获取本周热门条目"""
    service = HotListService(db)
    
    try:
        items = await service.get_trending_items(
            hours=168,  # 7天
            limit=limit
        )
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取本周热门失败: {str(e)}")


@router.get("/search/", response_model=HotItemListResponse)
async def search_hot_items(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    db: AsyncSession = Depends(get_db),
    platform_name: Optional[str] = Query(None, description="平台名称"),
    category_name: Optional[str] = Query(None, description="分类名称"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    hours: Optional[int] = Query(None, ge=1, le=168, description="最近N小时内的数据")
):
    """搜索热榜条目"""
    service = HotListService(db)
    
    # 构建搜索条件
    filters = {'search_query': q}
    if platform_name:
        filters['platform_name'] = platform_name
    if category_name:
        filters['category_name'] = category_name
    if hours:
        filters['crawled_after'] = datetime.utcnow() - timedelta(hours=hours)
    
    # 分页参数
    pagination = PaginationParams(page=page, size=size)
    
    try:
        result = await service.search_hot_items(filters, pagination)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/stats/summary")
async def get_stats_summary(
    db: AsyncSession = Depends(get_db)
):
    """获取统计摘要"""
    service = HotListService(db)
    
    try:
        stats = await service.get_stats_summary()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.get("/stats/platform/{platform_name}")
async def get_platform_stats(
    platform_name: str,
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=30, description="统计天数")
):
    """获取平台统计数据"""
    service = HotListService(db)
    
    try:
        stats = await service.get_platform_stats(platform_name, days)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取平台统计失败: {str(e)}")