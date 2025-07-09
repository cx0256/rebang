"""爬虫管理器"""
from typing import List, Dict, Any, Type
from datetime import datetime
import asyncio
import logging
logger = logging.getLogger(__name__)
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
        for crawler_name in self.crawlers.keys():
            task = asyncio.create_task(
                self.crawl_single(crawler_name),
                name=crawler_name
            )
            tasks.append((crawler_name, task))
        
        results = {}
        for crawler_name, task in tasks:
            try:
                items = await task
                results[crawler_name] = items
            except Exception as e:
                logger.error(f"爬虫任务 {crawler_name} 失败: {e}")
                results[crawler_name] = []
        
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
                                tags=item.tags,
                                crawled_at=datetime.now()
                            )
                            db.add(hot_item)
                            existing_urls.add(item.url)  # 添加到已存在URL集合中
                            new_items_count += 1
                    
                    # 清理旧数据，只保留最新的30条
                    from sqlalchemy import desc
                    stmt = select(HotItemModel).where(
                        HotItemModel.category_id == category.id
                    ).order_by(desc(HotItemModel.crawled_at)).offset(30)
                    result = await db.execute(stmt)
                    old_items = result.scalars().all()
                    
                    for old_item in old_items:
                        await db.delete(old_item)
                    
                    await db.commit()
                    logger.info(f"保存 {crawler_name} 数据: 新增 {new_items_count} 条, 更新 {updated_items_count} 条, 删除 {len(old_items)} 条旧数据")
                
            except Exception as e:
                logger.error(f"保存数据到数据库失败: {e}")
                await db.rollback()
            finally:
                break
    
    def _parse_crawler_name(self, crawler_name: str) -> tuple:
        """解析爬虫名称获取平台和分类"""
        mapping = {
            'nga_zatan': ('NGA', '杂谈'),
            'zhihu_hot': ('知乎', '热榜'),
            'weibo_hot': ('微博', '热榜'),
            'toutiao_hot': ('今日头条', '热榜'),
            'bilibili_hot': ('哔哩哔哩', '热榜'),
            'hupu_hot': ('虎扑', '热榜'),
            'ithome_hot': ('IT之家', '热榜'),
            'zol_hot': ('中关村在线', '热榜'),
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
            platform_data = {
                'NGA': {
                    'display_name': 'NGA玩家社区',
                    'base_url': 'https://bbs.nga.cn',
                    'description': 'NGA玩家社区热门讨论'
                },
                '知乎': {
                    'display_name': '知乎',
                    'base_url': 'https://www.zhihu.com',
                    'description': '知乎热榜内容'
                },
                '微博': {
                    'display_name': '新浪微博',
                    'base_url': 'https://weibo.com',
                    'description': '微博热搜榜'
                },
                '今日头条': {
                    'display_name': '今日头条',
                    'base_url': 'https://www.toutiao.com',
                    'description': '今日头条热榜'
                },
                '哔哩哔哩': {
                    'display_name': '哔哩哔哩',
                    'base_url': 'https://www.bilibili.com',
                    'description': 'B站热门视频榜'
                },
                '虎扑': {
                    'display_name': '虎扑体育',
                    'base_url': 'https://bbs.hupu.com',
                    'description': '虎扑热门话题'
                },
                'IT之家': {
                    'display_name': 'IT之家',
                    'base_url': 'https://www.ithome.com',
                    'description': 'IT之家热门资讯'
                },
                '中关村在线': {
                    'display_name': '中关村在线',
                    'base_url': 'https://www.zol.com.cn',
                    'description': '中关村在线热门内容'
                }
            }
            
            data = platform_data.get(name, {
                'display_name': name,
                'base_url': '',
                'description': f'{name}平台'
            })
            
            platform = Platform(
                name=name,
                display_name=data['display_name'],
                base_url=data['base_url'],
                description=data['description']
            )
            db.add(platform)
            await db.flush()  # 获取ID
        
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
            category = Category(
                platform_id=platform_id,
                name=name,
                display_name=name
            )
            db.add(category)
            await db.flush()  # 获取ID
        
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