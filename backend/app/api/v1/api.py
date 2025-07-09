from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

from app.api.v1.endpoints import (
    platforms,
    categories,
    hot_items,
    crawl_tasks,
    auth,
    admin,
    crawlers
)

# 创建API路由器
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(
    platforms.router,
    prefix="/platforms",
    tags=["platforms"]
)

api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["categories"]
)

api_router.include_router(
    hot_items.router,
    prefix="/hot-items",
    tags=["hot-items"]
)

api_router.include_router(
    crawl_tasks.router,
    prefix="/crawl-tasks",
    tags=["crawl-tasks"]
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"]
)

api_router.include_router(
    crawlers.router,
    prefix="/crawlers",
    tags=["crawlers"]
)

# 聚合热榜路由
@api_router.get("/hot", tags=["hot-lists"])
async def get_all_hot_lists(db: AsyncSession = Depends(get_db)):
    """获取所有平台的热榜数据"""
    from app.services.hot_list_service import HotListService
    from loguru import logger
    
    logger.info("API endpoint /hot called")
    service = HotListService(db)
    logger.info("HotListService created, calling get_all_hot_lists")
    result = await service.get_all_hot_lists()
    logger.info(f"Service returned result: {type(result)}, keys: {result.keys() if isinstance(result, dict) else 'not dict'}")
    return result


@api_router.get("/hot/{platform_name}", tags=["hot-lists"])
async def get_platform_hot_list(platform_name: str, db: AsyncSession = Depends(get_db)):
    """获取指定平台的热榜数据"""
    from app.services.hot_list_service import HotListService
    
    service = HotListService(db)
    return await service.get_platform_hot_list(platform_name)


@api_router.get("/hot/{platform_name}/{category_name}", tags=["hot-lists"])
async def get_category_hot_list(platform_name: str, category_name: str, db: AsyncSession = Depends(get_db)):
    """获取指定平台分类的热榜数据"""
    from app.services.hot_list_service import HotListService
    
    service = HotListService(db)
    return await service.get_category_hot_list(platform_name, category_name)