"""爬虫管理器"""
from typing import List, Dict, Any, Type
from datetime import datetime
import asyncio
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseCrawler, HotItem
from .nga_crawler import NGACrawler
from .zhihu_crawler import ZhihuCrawler
from .weibo_crawler import WeiboCrawler
from .toutiao_crawler import ToutiaoCrawler
from .bilibili_crawler import BiliBiliCrawler
from .hupu_crawler import HupuCrawler
from .ithome_crawler import ITHomeCrawler
from .zol_crawler import ZOLCrawler
from .smzdm_crawler import SmzdmCrawler
from .kr36_crawler import Kr36Crawler
from .baidu_crawler import BaiduCrawler
from app.core.database import get_db
from app.models.platform import Platform
from app.models.category import Category
from app.models.hot_item import HotItem as HotItemModel
from app.core.redis import redis_manager


class CrawlerManager:
    """爬虫管理器"""
    
    def __init__(self):
        self.crawlers: Dict[str, Type[BaseCrawler]] = {
            'nga_zatan': NGACrawler,
            'zhihu_hot': ZhihuCrawler,
            'weibo_hot': WeiboCrawler,
            'toutiao_hot': ToutiaoCrawler,
            'bilibili_hot': BiliBiliCrawler,
            'hupu_hot': HupuCrawler,
            'ithome_hot': ITHomeCrawler,
            'zol_hot': ZOLCrawler,
            'smzdm_hot': SmzdmCrawler,
            'kr36_hot': Kr36Crawler,
            'baidu_hot': BaiduCrawler,
        }
    
    def register_crawler(self, name: str, crawler_class: Type[BaseCrawler]):
        """注册新的爬虫"""
        self.crawlers[name] = crawler_class
        logger.info(f"注册爬虫: {name}")
    
    async def crawl_single(self, crawler_name: str) -> List[HotItem]:
        """执行单个爬虫"""
        if crawler_name not in self.crawlers:
            logger.error(f"未找到爬虫: {crawler_name}")
            return []
        
        crawler_class = self.crawlers[crawler_name]
        crawler = crawler_class()
        
        try:
            items = await crawler.run()
            logger.info(f"爬虫 {crawler_name} 完成，获取 {len(items)} 条数据")
            return items
        except Exception as e:
            logger.error(f"爬虫 {crawler_name} 执行失败: {e}")
            return []
    
    async def crawl_all(self) -> Dict[str, List[HotItem]]:
        """执行所有爬虫"""
        logger.info("开始执行所有爬虫任务")
        
        tasks = []
        for crawler_name, crawler_instance in self.crawlers.items():
            tasks.append(self.crawl_single(crawler_name))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_results = {}
        for i, result in enumerate(results):
            crawler_name = list(self.crawlers.keys())[i]
            if isinstance(result, Exception):
                logger.error(f"爬虫 {crawler_name} 失败: {result}", exc_info=True)
                all_results[crawler_name] = []
            else:
                all_results[crawler_name] = result
        
        return all_results
        
        total_items = sum(len(items) for items in results.values())
        logger.info(f"所有爬虫任务完成，共获取 {total_items} 条数据")
        
        return results
    
    async def save_to_database(self, crawler_results: Dict[str, List[HotItem]]):
        """保存爬取结果到数据库"""
        async for db in get_db():
            try:
                for crawler_name, items in crawler_results.items():
                    if not items:
                        continue
                    
                    # 获取或创建平台和分类
                    platform_name, category_name = self._parse_crawler_name(crawler_name)
                    platform = await self._get_or_create_platform(db, platform_name)
                    category = await self._get_or_create_category(db, platform.id, category_name)
                    
                    # 查询当前分类下的所有热榜条目URL，用于去重
                    from sqlalchemy import select
                    stmt = select(HotItemModel.url).where(HotItemModel.category_id == category.id)
                    result = await db.execute(stmt)
                    existing_urls = {row[0] for row in result.fetchall()}
                    
                    # 保存热榜条目（去重）
                    new_items_count = 0
                    updated_items_count = 0
                    
                    for item in items:
                        # 检查URL是否已存在
                        if item.url in existing_urls:
                            # 更新已存在的条目（仅更新排名和热度）
                            stmt = select(HotItemModel).where(
                                HotItemModel.category_id == category.id,
                                HotItemModel.url == item.url
                            )
                            result = await db.execute(stmt)
                            existing_item = result.scalar_one_or_none()
                            
                            if existing_item:
                                existing_item.rank_position = item.rank
                                existing_item.score = int(item.hot_value) if item.hot_value and item.hot_value.isdigit() else 0
                                existing_item.comment_count = item.comment_count or 0
                                existing_item.crawled_at = datetime.now()
                                updated_items_count += 1
                        else:
                            # 创建新条目
                            hot_item = HotItemModel(
                                category_id=category.id,
                                title=item.title,
                                url=item.url,
                                rank_position=item.rank,
                                score=int(item.hot_value) if item.hot_value and item.hot_value.isdigit() else 0,
                                author=item.author,
                                comment_count=item.comment_count or 0,
                                description=item.summary,
                                published_at=item.publish_time,
                                tags=item.tags if item.tags else None,
                                crawled_at=datetime.now()
                            )
                            db.add(hot_item)
                            new_items_count += 1

                    if new_items_count > 0 or updated_items_count > 0:
                        try:
                            # 清理旧数据
                            from sqlalchemy import desc
                            stmt = select(HotItemModel.id).where(
                                HotItemModel.category_id == category.id
                            ).order_by(desc(HotItemModel.crawled_at)).offset(30)
                            result = await db.execute(stmt)
                            old_item_ids = [row[0] for row in result.fetchall()]
                            
                            if old_item_ids:
                                from sqlalchemy import delete
                                delete_stmt = delete(HotItemModel).where(HotItemModel.id.in_(old_item_ids))
                                await db.execute(delete_stmt)

                            await db.commit()
                            logger.info(f"保存 {crawler_name} 数据: 新增 {new_items_count} 条, 更新 {updated_items_count} 条, 删除 {len(old_item_ids)} 条旧数据")
                        except Exception as e:
                            logger.error(f"提交事务失败: {e}")
                            await db.rollback()

            except Exception as e:
                logger.error(f"保存数据到数据库失败: {e}")
                await db.rollback()
            finally:
                break
    
    def _parse_crawler_name(self, crawler_name: str) -> tuple:
        """解析爬虫名称获取平台和分类"""
        mapping = {
            'nga_zatan': ('nga', 'zatan'),
            'zhihu_hot': ('zhihu', 'hot'),
            'weibo_hot': ('weibo', 'hot'),
            'toutiao_hot': ('toutiao', 'hot'),
            'bilibili_hot': ('bilibili', 'popular'),
            'hupu_hot': ('hupu', 'hot'),
            'ithome_hot': ('ithome', 'hot'),
            'zol_hot': ('zol', 'hot'),
            'smzdm_hot': ('smzdm', 'hot'),
            'kr36_hot': ('36kr', 'hot'),
            'baidu_hot': ('baidu', 'hot'),
        }
        return mapping.get(crawler_name, ('Unknown', 'Unknown'))
    
    async def _get_or_create_platform(self, db: AsyncSession, name: str) -> Platform:
        """获取或创建平台"""
        from sqlalchemy import select
        
        # 查找现有平台
        stmt = select(Platform).where(Platform.name == name)
        result = await db.execute(stmt)
        platform = result.scalar_one_or_none()
        
        if not platform:
            # 创建新平台
            platform_display_name_map = {
                'nga': 'NGA玩家社区',
                'zhihu': '知乎',
                'weibo': '微博',
                'toutiao': '今日头条',
                'bilibili': 'B站',
                'hupu': '虎扑',
                'ithome': 'IT之家',
                'zol': '中关村在线',
            }
            display_name = platform_display_name_map.get(name, name)
            
            platform = Platform(
                name=name,
                display_name=display_name,
                # 其他字段可以根据需要设置默认值
            )
            db.add(platform)
            await db.flush()  # 立即获取ID

        return platform
    
    async def _get_or_create_category(self, db: AsyncSession, platform_id: int, name: str) -> Category:
        """获取或创建分类"""
        from sqlalchemy import select
        
        # 查找现有分类
        stmt = select(Category).where(
            Category.platform_id == platform_id,
            Category.name == name
        )
        result = await db.execute(stmt)
        category = result.scalar_one_or_none()
        
        if not category:
            # 创建新分类
            category_display_name_map = {
                'hot': '热榜',
                'zatan': '杂谈',
                'popular': '热门',
                # 根据需要添加更多映射
            }
            display_name = category_display_name_map.get(name, name.capitalize())

            category = Category(
                platform_id=platform_id,
                name=name,
                display_name=display_name
            )
            db.add(category)
            await db.flush()  # 立即获取ID
            
        return category
    
    async def run_crawl_task(self):
        """运行爬取任务"""
        try:
            # 执行所有爬虫
            results = await self.crawl_all()
            
            # 保存到数据库
            await self.save_to_database(results)
            
            # 清除相关缓存
            await self._clear_cache()
            
            logger.info("爬取任务完成")
            
        except Exception as e:
            logger.error(f"爬取任务执行失败: {e}")
    
    async def _clear_cache(self):
        """清除相关缓存"""
        try:
            # 清除热榜相关的缓存
            cache_patterns = [
                "hot_list:*",
                "hot_items:*",
                "platforms:*",
                "categories:*"
            ]
            
            for pattern in cache_patterns:
                await redis_manager.delete_pattern(pattern)
            
            logger.info("缓存清除完成")
        except Exception as e:
            logger.warning(f"清除缓存失败: {e}")


# 全局爬虫管理器实例
crawler_manager = CrawlerManager()