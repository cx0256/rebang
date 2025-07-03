import asyncio
import logging
from app.core.database import init_db
from app.crawlers.crawler_manager import CrawlerManager
# 确保所有模型都被导入，这样Base.metadata.create_all才能找到它们
from app.models.platform import Platform
from app.models.category import Category
from app.models.hot_item import HotItem
from app.models import *  # 导入所有模型

async def main():
    """运行爬虫并保存数据"""
    try:
        # 初始化数据库
        logger.info("初始化数据库...")
        await init_db()
        
        # 创建爬虫管理器
        crawler_manager = CrawlerManager()
        
        # 运行NGA爬虫
        logger.info("开始运行NGA爬虫...")
        nga_results = await crawler_manager.crawl_single('nga_zatan')
        logger.info(f"NGA爬虫获取到 {len(nga_results)} 条数据")
        
        # 保存到数据库
        if nga_results:
            logger.info("保存NGA数据到数据库...")
            await crawler_manager.save_to_database({'nga_zatan': nga_results})
            logger.info("NGA数据保存完成")
        
        # 运行所有爬虫
        logger.info("开始运行所有爬虫...")
        all_results = await crawler_manager.crawl_all()
        
        # 保存所有数据
        logger.info("保存所有数据到数据库...")
        await crawler_manager.save_to_database(all_results)
        
        total_items = sum(len(items) for items in all_results.values())
        logger.info(f"所有爬虫完成，共获取并保存 {total_items} 条数据")
        
    except Exception as e:
        logger.error(f"运行爬虫失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())