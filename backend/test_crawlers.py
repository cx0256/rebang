#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试爬虫脚本"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.crawlers.zhihu_crawler import ZhihuCrawler
from app.crawlers.hupu_crawler import HupuCrawler
from app.crawlers.ithome_crawler import ITHomeCrawler
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_zhihu_crawler():
    """测试知乎爬虫"""
    logger.info("开始测试知乎爬虫...")
    crawler = ZhihuCrawler()
    try:
        items = await crawler.run()
        logger.info(f"知乎爬虫测试完成，获取到 {len(items)} 条数据")
        if items:
            logger.info("前3条数据:")
            for i, item in enumerate(items[:3]):
                logger.info(f"  {i+1}. {item.title} - {item.url}")
        return items
    except Exception as e:
        logger.error(f"知乎爬虫测试失败: {e}")
        import traceback
        traceback.print_exc()
        return []

async def test_hupu_crawler():
    """测试虎扑爬虫"""
    logger.info("开始测试虎扑爬虫...")
    crawler = HupuCrawler()
    try:
        items = await crawler.run()
        logger.info(f"虎扑爬虫测试完成，获取到 {len(items)} 条数据")
        if items:
            logger.info("前3条数据:")
            for i, item in enumerate(items[:3]):
                logger.info(f"  {i+1}. {item.title} - {item.url}")
        return items
    except Exception as e:
        logger.error(f"虎扑爬虫测试失败: {e}")
        import traceback
        traceback.print_exc()
        return []

async def test_ithome_crawler():
    """测试IT之家爬虫"""
    logger.info("开始测试IT之家爬虫...")
    crawler = ITHomeCrawler()
    try:
        items = await crawler.run()
        logger.info(f"IT之家爬虫测试完成，获取到 {len(items)} 条数据")
        if items:
            logger.info("前3条数据:")
            for i, item in enumerate(items[:3]):
                logger.info(f"  {i+1}. {item.title} - {item.url}")
        return items
    except Exception as e:
        logger.error(f"IT之家爬虫测试失败: {e}")
        import traceback
        traceback.print_exc()
        return []

async def main():
    """主函数"""
    logger.info("开始测试所有爬虫...")
    
    # 测试知乎爬虫
    zhihu_items = await test_zhihu_crawler()
    print("\n" + "="*50 + "\n")
    
    # 测试虎扑爬虫
    hupu_items = await test_hupu_crawler()
    print("\n" + "="*50 + "\n")
    
    # 测试IT之家爬虫
    ithome_items = await test_ithome_crawler()
    
    # 总结
    print("\n" + "="*50)
    print("测试总结:")
    print(f"知乎爬虫: {len(zhihu_items)} 条数据")
    print(f"虎扑爬虫: {len(hupu_items)} 条数据")
    print(f"IT之家爬虫: {len(ithome_items)} 条数据")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())