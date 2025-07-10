#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from backend.app.crawlers.nga_crawler import NGACrawler

async def test_crawler():
    """测试NGA爬虫功能"""
    print("🕷️ 测试爬虫功能")
    
    try:
        crawler = NGACrawler()
        items = await crawler.crawl()
        
        if items:
            print(f"✅ 爬虫测试成功 - 获取到 {len(items)} 条数据")
            
            # 显示前5条
            for i, item in enumerate(items[:5], 1):
                print(f"   {i}. {item.title[:60]}...")
                print(f"      作者: {item.author or 'Unknown'}")
                print(f"      链接: {item.url}")
                print()
            return True
        else:
            print("⚠️ 爬虫测试失败 - 未获取到数据")
            return False
    
    except Exception as e:
        print(f"❌ 爬虫测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    asyncio.run(test_crawler())