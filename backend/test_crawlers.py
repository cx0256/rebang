#!/usr/bin/env python3
"""爬虫测试脚本"""
import sys
import os
import asyncio
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.crawlers.nga_crawler import NGACrawler
from app.crawlers.zhihu_crawler import ZhihuCrawler
from app.crawlers.weibo_crawler import WeiboCrawler
from app.crawlers.toutiao_crawler import ToutiaoCrawler
from app.crawlers.bilibili_crawler import BiliBiliCrawler
from app.crawlers.hupu_crawler import HupuCrawler
from app.crawlers.ithome_crawler import ITHomeCrawler
from app.crawlers.zol_crawler import ZOLCrawler
from app.crawlers.crawler_manager import CrawlerManager
from loguru import logger


async def test_nga_crawler():
    """测试NGA爬虫"""
    logger.info("开始测试NGA爬虫...")
    
    crawler = NGACrawler()
    items = await crawler.run()
    
    logger.info(f"NGA爬虫测试完成，获取到 {len(items)} 条数据")
    
    if items:
        logger.info("前3条数据示例:")
        for i, item in enumerate(items[:3], 1):
            logger.info(f"{i}. {item.title} - {item.url}")
    
    return items


async def test_zhihu_crawler():
    """测试知乎爬虫"""
    logger.info("开始测试知乎爬虫...")
    
    crawler = ZhihuCrawler()
    items = await crawler.run()
    
    logger.info(f"知乎爬虫测试完成，获取到 {len(items)} 条数据")
    
    if items:
        logger.info("前3条数据示例:")
        for i, item in enumerate(items[:3], 1):
            logger.info(f"{i}. {item.title} - 热度: {item.hot_value}")
    
    return items


async def test_weibo_crawler():
    """测试微博爬虫"""
    logger.info("开始测试微博爬虫...")
    
    crawler = WeiboCrawler()
    items = await crawler.run()
    
    logger.info(f"微博爬虫测试完成，获取到 {len(items)} 条数据")
    
    if items:
        logger.info("前3条数据示例:")
        for i, item in enumerate(items[:3], 1):
            logger.info(f"{i}. {item.title} - 热度: {item.hot_value}")
    
    return items


async def test_toutiao_crawler():
    """测试今日头条爬虫"""
    logger.info("开始测试今日头条爬虫...")
    
    crawler = ToutiaoCrawler()
    items = await crawler.run()
    
    logger.info(f"今日头条爬虫测试完成，获取到 {len(items)} 条数据")
    
    if items:
        logger.info("前3条数据示例:")
        for i, item in enumerate(items[:3], 1):
            logger.info(f"{i}. {item.title} - {item.url}")
    
    return items


async def test_bilibili_crawler():
    """测试B站爬虫"""
    logger.info("开始测试B站爬虫...")
    
    crawler = BiliBiliCrawler()
    items = await crawler.run()
    
    logger.info(f"B站爬虫测试完成，获取到 {len(items)} 条数据")
    
    if items:
        logger.info("前3条数据示例:")
        for i, item in enumerate(items[:3], 1):
            logger.info(f"{i}. {item.title} - 作者: {item.author}")
    
    return items


async def test_hupu_crawler():
    """测试虎扑爬虫"""
    logger.info("开始测试虎扑爬虫...")
    
    crawler = HupuCrawler()
    items = await crawler.run()
    
    logger.info(f"虎扑爬虫测试完成，获取到 {len(items)} 条数据")
    
    if items:
        logger.info("前3条数据示例:")
        for i, item in enumerate(items[:3], 1):
            logger.info(f"{i}. {item.title} - 作者: {item.author}")
    
    return items


async def test_ithome_crawler():
    """测试IT之家爬虫"""
    logger.info("开始测试IT之家爬虫...")
    
    crawler = ITHomeCrawler()
    items = await crawler.run()
    
    logger.info(f"IT之家爬虫测试完成，获取到 {len(items)} 条数据")
    
    if items:
        logger.info("前3条数据示例:")
        for i, item in enumerate(items[:3], 1):
            logger.info(f"{i}. {item.title} - {item.url}")
    
    return items


async def test_zol_crawler():
    """测试中关村在线爬虫"""
    logger.info("开始测试中关村在线爬虫...")
    
    crawler = ZOLCrawler()
    items = await crawler.run()
    
    logger.info(f"中关村在线爬虫测试完成，获取到 {len(items)} 条数据")
    
    if items:
        logger.info("前3条数据示例:")
        for i, item in enumerate(items[:3], 1):
            logger.info(f"{i}. {item.title} - {item.url}")
    
    return items


async def test_crawler_manager():
    """测试爬虫管理器"""
    logger.info("开始测试爬虫管理器...")
    
    # 创建爬虫管理器实例
    crawler_manager = CrawlerManager()
    
    # 测试单个爬虫
    nga_items = await crawler_manager.crawl_single('nga_zatan')
    logger.info(f"NGA爬虫通过管理器获取到 {len(nga_items)} 条数据")
    
    zhihu_items = await crawler_manager.crawl_single('zhihu_hot')
    logger.info(f"知乎爬虫通过管理器获取到 {len(zhihu_items)} 条数据")
    
    weibo_items = await crawler_manager.crawl_single('weibo_hot')
    logger.info(f"微博爬虫通过管理器获取到 {len(weibo_items)} 条数据")
    
    bilibili_items = await crawler_manager.crawl_single('bilibili_hot')
    logger.info(f"B站爬虫通过管理器获取到 {len(bilibili_items)} 条数据")
    
    # 测试所有爬虫
    all_results = await crawler_manager.crawl_all()
    total_items = sum(len(items) for items in all_results.values())
    logger.info(f"所有爬虫通过管理器获取到 {total_items} 条数据")
    
    return all_results


async def main():
    """主函数"""
    logger.info("开始爬虫功能测试")
    
    try:
        # 测试单个爬虫
        await test_nga_crawler()
        await test_zhihu_crawler()
        await test_weibo_crawler()
        await test_toutiao_crawler()
        await test_bilibili_crawler()
        await test_hupu_crawler()
        await test_ithome_crawler()
        await test_zol_crawler()
        
        # 测试爬虫管理器
        await test_crawler_manager()
        
        logger.info("所有测试完成")
        
    except Exception as e:
        logger.error(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 配置日志
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # 运行测试
    asyncio.run(main())