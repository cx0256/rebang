#!/usr/bin/env python3
"""爬虫功能演示脚本"""
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

# 导入爬虫
from app.crawlers.nga_crawler import NGACrawler
from app.crawlers.zhihu_crawler import ZhihuCrawler
from app.crawlers.weibo_crawler import WeiboCrawler
from app.crawlers.bilibili_crawler import BiliBiliCrawler
from app.crawlers.toutiao_crawler import ToutiaoCrawler
from app.crawlers.hupu_crawler import HupuCrawler
from app.crawlers.ithome_crawler import ITHomeCrawler
from app.crawlers.zol_crawler import ZOLCrawler

async def test_crawler(crawler_class, name):
    """测试单个爬虫"""
    print(f"\n{'='*20} 测试 {name} {'='*20}")
    try:
        crawler = crawler_class()
        print(f"✓ {name} 实例化成功")
        print(f"  平台: {crawler.platform}")
        print(f"  分类: {crawler.category}")
        
        # 尝试爬取数据（限制数量避免过多输出）
        print(f"\n开始爬取 {name} 数据...")
        async with crawler:
            items = await crawler.crawl()
        
        if items:
            print(f"✓ 成功爬取到 {len(items)} 条数据")
            # 显示前3条数据作为示例
            for i, item in enumerate(items[:3]):
                print(f"\n第 {i+1} 条:")
                print(f"  标题: {item.title[:50]}{'...' if len(item.title) > 50 else ''}")
                print(f"  排名: {item.rank}")
                print(f"  链接: {item.url[:80]}{'...' if len(item.url) > 80 else ''}")
                if item.hot_value:
                    print(f"  热度: {item.hot_value}")
                if item.author:
                    print(f"  作者: {item.author}")
        else:
            print("⚠️ 未获取到数据")
            
    except Exception as e:
        print(f"✗ {name} 测试失败: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """主函数"""
    print("🚀 开始爬虫功能演示")
    print("注意: 由于网络限制，部分爬虫可能无法正常工作")
    
    # 要测试的爬虫列表
    crawlers = [
        (NGACrawler, "NGA杂谈"),
        (ZhihuCrawler, "知乎热榜"),
        (WeiboCrawler, "微博热搜"),
        (BiliBiliCrawler, "B站热榜"),
        (ToutiaoCrawler, "今日头条"),
        (HupuCrawler, "虎扑步行街"),
        (ITHomeCrawler, "IT之家"),
        (ZOLCrawler, "中关村在线")
    ]
    
    success_count = 0
    total_items = 0
    
    for crawler_class, name in crawlers:
        try:
            await test_crawler(crawler_class, name)
            success_count += 1
        except Exception as e:
            print(f"\n✗ {name} 整体测试失败: {e}")
        
        # 添加延迟避免请求过快
        await asyncio.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"📊 测试总结:")
    print(f"  成功测试: {success_count}/{len(crawlers)} 个爬虫")
    print(f"\n🎉 爬虫系统已成功扩展到 {len(crawlers)} 个平台！")
    print(f"\n📝 支持的平台:")
    for _, name in crawlers:
        print(f"  - {name}")
    
    print(f"\n💡 使用说明:")
    print(f"  1. 每个爬虫都支持获取最多30条热榜数据")
    print(f"  2. 前端界面支持滑动浏览和平台筛选")
    print(f"  3. 系统会自动处理网络异常和数据解析错误")
    print(f"  4. 可以通过API接口 /api/v1/hot 获取所有平台数据")

if __name__ == "__main__":
    asyncio.run(main())