from typing import List, Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload
from loguru import logger
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.redis import redis_manager, cache_result
from app.core.config import settings
from app.models.platform import Platform
from app.models.category import Category
from app.models.hot_item import HotItem


class HotListService:
    """热榜服务类"""
    
    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db
    
    async def _get_db(self) -> AsyncSession:
        """获取数据库会话"""
        if self.db:
            return self.db
        async for db in get_db():
            return db
    
    @cache_result("hot_list:all", expire=settings.HOT_LIST_CACHE_TIME)
    async def get_all_hot_lists(self) -> Dict[str, Any]:
        """获取所有平台的热榜数据"""
        try:
            db = await self._get_db()
            
            # 查询所有活跃平台及其分类和热榜数据
            stmt = (
                select(Platform)
                .options(
                    selectinload(Platform.categories).selectinload(Category.hot_items)
                )
                .where(Platform.is_active == True)
                .order_by(Platform.id)
            )
            
            result = await db.execute(stmt)
            platforms = result.scalars().all()
            
            # 构建响应数据
            hot_lists = []
            total_items = 0
            
            for platform in platforms:
                platform_data = {
                    "platform": platform.to_dict(),
                    "categories": []
                }
                
                for category in platform.categories:
                    if not category.is_active:
                        continue
                    
                    # 获取最新的热榜数据（最近24小时内）
                recent_time = datetime.utcnow() - timedelta(hours=24)
                    recent_items = [
                        item for item in category.hot_items
                        if item.crawled_at and item.crawled_at >= recent_time
                    ]
                    
                    # 按排名排序
                    recent_items.sort(key=lambda x: x.rank_position or 999)
                    
                    category_data = {
                        "category": category.to_simple_dict(),
                        "items": [item.to_list_dict() for item in recent_items[:50]],
                        "total_count": len(recent_items),
                        "last_updated": max(
                            [item.crawled_at for item in recent_items],
                            default=None
                        ).isoformat() if recent_items else None
                    }
                    
                    platform_data["categories"].append(category_data)
                    total_items += len(recent_items)
                
                if platform_data["categories"]:
                    hot_lists.append(platform_data)
            
            return {
                "success": True,
                "data": hot_lists,
                "total_platforms": len(hot_lists),
                "total_items": total_items,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取所有热榜失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": []
            }
    
    @cache_result("hot_list:platform", expire=settings.HOT_LIST_CACHE_TIME)
    async def get_platform_hot_list(self, platform_name: str) -> Dict[str, Any]:
        """获取指定平台的热榜数据"""
        try:
            db = await self._get_db()
            
            # 查询指定平台
            stmt = (
                select(Platform)
                .options(
                    selectinload(Platform.categories).selectinload(Category.hot_items)
                )
                .where(
                    and_(
                        Platform.name == platform_name,
                        Platform.is_active == True
                    )
                )
            )
            
            result = await db.execute(stmt)
            platform = result.scalar_one_or_none()
            
            if not platform:
                return {
                    "success": False,
                    "error": f"平台 '{platform_name}' 不存在或未启用",
                    "data": None
                }
            
            # 构建响应数据
            categories = []
            total_items = 0
            
            for category in platform.categories:
                if not category.is_active:
                    continue
                
                # 获取最新的热榜数据
        recent_time = datetime.utcnow() - timedelta(hours=24)
                recent_items = [
                    item for item in category.hot_items
                    if item.crawled_at and item.crawled_at >= recent_time
                ]
                
                # 按排名排序
                recent_items.sort(key=lambda x: x.rank_position or 999)
                
                category_data = {
                    "category": category.to_simple_dict(),
                    "items": [item.to_list_dict() for item in recent_items[:50]],
                    "total_count": len(recent_items),
                    "last_updated": max(
                        [item.crawled_at for item in recent_items],
                        default=None
                    ).isoformat() if recent_items else None
                }
                
                categories.append(category_data)
                total_items += len(recent_items)
            
            return {
                "success": True,
                "data": {
                    "platform": platform.to_dict(),
                    "categories": categories,
                    "total_items": total_items
                },
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取平台 {platform_name} 热榜失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    @cache_result("hot_list:category", expire=settings.HOT_LIST_CACHE_TIME)
    async def get_category_hot_list(
        self, 
        platform_name: str, 
        category_name: str
    ) -> Dict[str, Any]:
        """获取指定平台分类的热榜数据"""
        try:
            db = await self._get_db()
            
            # 查询指定分类
            stmt = (
                select(Category)
                .join(Platform)
                .options(selectinload(Category.hot_items))
                .where(
                    and_(
                        Platform.name == platform_name,
                        Category.name == category_name,
                        Platform.is_active == True,
                        Category.is_active == True
                    )
                )
            )
            
            result = await db.execute(stmt)
            category = result.scalar_one_or_none()
            
            if not category:
                return {
                    "success": False,
                    "error": f"分类 '{platform_name}/{category_name}' 不存在或未启用",
                    "data": None
                }
            
            # 获取最新的热榜数据
            recent_time = datetime.utcnow() - timedelta(hours=24)
            recent_items = [
                item for item in category.hot_items
                if item.crawled_at and item.crawled_at >= recent_time
            ]
            
            # 按排名排序
            recent_items.sort(key=lambda x: x.rank_position or 999)
            
            return {
                "success": True,
                "data": {
                    "category": category.to_dict(),
                    "items": [item.to_dict() for item in recent_items],
                    "total_count": len(recent_items),
                    "last_updated": max(
                        [item.crawled_at for item in recent_items],
                        default=None
                    ).isoformat() if recent_items else None
                }
            }
            
        except Exception as e:
            logger.error(f"获取分类 {platform_name}/{category_name} 热榜失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    async def get_trending_items(
        self, 
        hours: int = 24, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取热门趋势条目"""
        try:
            db = await self._get_db()
            
            # 计算时间范围
            since_time = datetime.utcnow() - timedelta(hours=hours)
            
            # 查询热门条目（按热度分数排序）
            stmt = (
                select(HotItem)
                .join(Category)
                .join(Platform)
                .where(
                    and_(
                        HotItem.crawled_at >= since_time,
                        Category.is_active == True,
                        Platform.is_active == True
                    )
                )
                .order_by(desc(HotItem.score), desc(HotItem.comment_count))
                .limit(limit)
            )
            
            result = await db.execute(stmt)
            items = result.scalars().all()
            
            return [item.to_dict() for item in items]
            
        except Exception as e:
            logger.error(f"获取热门趋势失败: {e}")
            return []
    
    async def refresh_cache(self) -> bool:
        """刷新缓存"""
        try:
            # 清除相关缓存
            cache_keys = await redis_manager.keys("hot_list:*")
            for key in cache_keys:
                await redis_manager.delete(key)
            
            logger.info("热榜缓存已刷新")
            return True
            
        except Exception as e:
            logger.error(f"刷新缓存失败: {e}")
            return False
    
    async def get_cache_status(self) -> Dict[str, Any]:
        """获取缓存状态"""
        try:
            cache_keys = await redis_manager.keys("hot_list:*")
            cache_info = []
            
            for key in cache_keys:
                ttl = await redis_manager.ttl(key)
                cache_info.append({
                    "key": key,
                    "ttl": ttl,
                    "expires_in": f"{ttl // 60}分{ttl % 60}秒" if ttl > 0 else "已过期"
                })
            
            return {
                "total_keys": len(cache_keys),
                "cache_info": cache_info
            }
            
        except Exception as e:
            logger.error(f"获取缓存状态失败: {e}")
            return {"error": str(e)}