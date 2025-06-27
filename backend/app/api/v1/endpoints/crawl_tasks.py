from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.services.hot_list_service import HotListService

router = APIRouter()


@router.get("/")
async def get_crawl_tasks(
    db: AsyncSession = Depends(get_db)
):
    """获取爬虫任务列表"""
    service = HotListService(db)
    try:
        tasks = await service.get_crawl_tasks()
        return {"success": True, "data": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_crawl_task(
    task_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """创建爬虫任务"""
    service = HotListService(db)
    try:
        task = await service.create_crawl_task(task_data)
        return {"success": True, "data": task}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}")
async def get_crawl_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个爬虫任务"""
    service = HotListService(db)
    try:
        task = await service.get_crawl_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"success": True, "data": task}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))