"""百度热搜爬虫"""
from typing import List
from datetime import datetime
import logging
import re
import json
import aiohttp

logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem

class BaiduCrawler(BaseCrawler):
    """百度热搜爬虫"""
    
    def __init__(self):
        super().__init__("百度", "热搜")
        self.hot_url = "https://top.baidu.com/board?tab=realtime"
        self.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/1.0 Mobile/12F69 Safari/605.1.15',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://top.baidu.com/',
        })
    
    async def crawl(self) -> List[HotItem]:
        """爬取百度热搜"""
        # 确保session已创建
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )
        
        try:
            logger.info(f"正在请求百度热搜: {self.hot_url}")
            
            async with self.session.get(self.hot_url) as response:
                if response.status == 200:
                    html = await response.text()
                    logger.info("成功获取百度热搜页面")
                    
                    items = []
                    
                    # 使用正则表达式提取数据
                    pattern = r'<!--s-data:(.*?)-->'
                    match = re.search(pattern, html, re.DOTALL)
                    
                    if match:
                        try:
                            json_str = match.group(1)
                            data = json.loads(json_str)
                            
                            # 提取热搜数据
                            if 'cards' in data and len(data['cards']) > 0:
                                content = data['cards'][0].get('content', [])
                                
                                for rank, item_data in enumerate(content[:30], 1):
                                    try:
                                        # 提取标题
                                        title = item_data.get('word', '').strip()
                                        if not title:
                                            continue
                                        
                                        # 构建搜索URL
                                        query = item_data.get('query', title)
                                        url = f"https://www.baidu.com/s?wd={query}"
                                        
                                        # 提取描述
                                        description = item_data.get('desc', '')
                                        
                                        # 提取热度
                                        hot_score = item_data.get('hotScore', 0)
                                        hot_value = str(hot_score) if hot_score else '0'
                                        
                                        # 提取图片
                                        image_url = item_data.get('img', '')
                                        
                                        # 提取显示信息（作者或来源）
                                        show_info = item_data.get('show', [])
                                        author = ' '.join(show_info) if show_info else ''
                                        
                                        # 提取原始URL（移动端）
                                        raw_url = item_data.get('rawUrl', '')
                                        
                                        item = HotItem(
                                            title=title,
                                            url=url,
                                            rank=rank,
                                            hot_value=hot_value,
                                            author=author if author else None,
                                            description=description if description else None,
                                            image_url=image_url if image_url else None,
                                            publish_time=datetime.now(),
                                            extra_data={
                                                'mobile_url': raw_url,
                                                'query': query,
                                                'index': item_data.get('index', rank)
                                            }
                                        )
                                        items.append(item)
                                        
                                    except Exception as e:
                                        logger.warning(f"解析百度热搜数据失败: {e}")
                                        continue
                            
                            logger.info(f"成功解析到 {len(items)} 条百度热搜")
                            return items
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"解析百度热搜JSON数据失败: {e}")
                            return []
                    else:
                        logger.error("未找到百度热搜数据")
                        return []
                    
                else:
                    logger.error(f"百度热搜请求失败，状态码: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"百度热搜请求异常: {e}")
            return []