#!/usr/bin/env python3
"""简化的爬虫测试脚本"""
import sys
import os
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

print("开始测试爬虫模块导入...")
print("="*50)

# 测试基础模块
try:
    from app.crawlers.base import BaseCrawler, HotItem
    print("✓ BaseCrawler 和 HotItem 导入成功")
except ImportError as e:
    print(f"✗ BaseCrawler 导入失败: {e}")
    print("缺少依赖库，请安装: pip install aiohttp beautifulsoup4")
    sys.exit(1)

# 测试各个爬虫
crawlers_to_test = [
    ('NGACrawler', 'app.crawlers.nga_crawler'),
    ('ZhihuCrawler', 'app.crawlers.zhihu_crawler'),
    ('WeiboCrawler', 'app.crawlers.weibo_crawler'),
    ('BiliBiliCrawler', 'app.crawlers.bilibili_crawler'),
    ('ToutiaoCrawler', 'app.crawlers.toutiao_crawler'),
    ('HupuCrawler', 'app.crawlers.hupu_crawler'),
    ('ITHomeCrawler', 'app.crawlers.ithome_crawler'),
    ('ZOLCrawler', 'app.crawlers.zol_crawler')
]

success_count = 0
failed_crawlers = []

for crawler_name, module_path in crawlers_to_test:
    try:
        module = __import__(module_path, fromlist=[crawler_name])
        crawler_class = getattr(module, crawler_name)
        print(f"✓ {crawler_name} 导入成功")
        success_count += 1
    except ImportError as e:
        print(f"✗ {crawler_name} 导入失败: {e}")
        failed_crawlers.append(crawler_name)
    except Exception as e:
        print(f"✗ {crawler_name} 其他错误: {e}")
        failed_crawlers.append(crawler_name)

print("\n" + "="*50)
print(f"测试结果: {success_count}/{len(crawlers_to_test)} 个爬虫导入成功")

if failed_crawlers:
    print(f"失败的爬虫: {', '.join(failed_crawlers)}")
    print("\n建议安装缺失的依赖:")
    print("pip install aiohttp beautifulsoup4 requests")
else:
    print("\n🎉 所有爬虫模块导入成功！")
    
    # 测试CrawlerManager（如果没有数据库依赖问题）
    try:
        from app.crawlers.crawler_manager import CrawlerManager
        print("\n✓ CrawlerManager 导入成功")
        
        # 创建实例（不连接数据库）
        manager = CrawlerManager()
        crawlers = manager.get_all_crawlers()
        print(f"✓ CrawlerManager 初始化成功，注册了 {len(crawlers)} 个爬虫:")
        for name in crawlers.keys():
            print(f"  - {name}")
    except ImportError as e:
        print(f"\n✗ CrawlerManager 导入失败: {e}")
        print("可能缺少数据库相关依赖")
    except Exception as e:
        print(f"\n✗ CrawlerManager 初始化失败: {e}")

print("\n测试完成！")