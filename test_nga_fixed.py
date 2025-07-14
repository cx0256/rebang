import asyncio
import sys
import os

# 添加项目路径到sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.crawlers.nga_crawler import NGACrawler

async def test_nga_crawler():
    """测试修复后的NGA爬虫"""
    try:
        print("初始化NGA爬虫...")
        crawler = NGACrawler()
        
        print("开始获取NGA热榜数据...")
        items = await crawler.crawl()
        
        if items:
            print(f"\n成功获取到 {len(items)} 条NGA热榜数据:")
            print("-" * 80)
            
            for i, item in enumerate(items[:5], 1):  # 显示前5条
                print(f"{i}. 标题: {item.title}")
                print(f"   链接: {item.url}")
                print(f"   作者: {item.author}")
                print(f"   回复数: {item.comment_count}")
                print(f"   发布时间: {item.publish_time}")
                print("-" * 80)
        else:
            print("未获取到任何数据，可能的原因:")
            print("1. NGA API接口访问失败")
            print("2. 网页解析回退也失败")
            print("3. 网络连接问题")
            
        # 关闭session
        if crawler.session:
            await crawler.session.close()
            
    except Exception as e:
        print(f"测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(test_nga_crawler())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            print("\n注意: 出现了 'Event loop is closed' 错误，这通常不影响实际功能")
        else:
            raise
    except Exception as e:
        print(f"运行测试时发生错误: {e}")