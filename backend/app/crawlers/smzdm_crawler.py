"""什么值得买爬虫"""
from typing import List
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem

class SmzdmCrawler(BaseCrawler):
    """什么值得买爬虫"""
    
    def __init__(self):
        super().__init__("什么值得买", "好价")
        self.hot_url = "https://www.smzdm.com/top/"
    
    async def crawl(self) -> List[HotItem]:
        """爬取什么值得买好价榜"""
        try:
            html = await self.fetch(self.hot_url)
            soup = self.parse_html(html)
            items = []
            rank = 1
            
            hot_list = soup.find('ul', class_='rank-list')
            if not hot_list:
                return []
            
            for item_li in hot_list.find_all('li', class_='rank-item')[:30]:
                try:
                    title_tag = item_li.find('a', class_='title')
                    if not title_tag:
                        continue
                    
                    title = title_tag.get_text(strip=True)
                    url = title_tag['href']
                    
                    hot_value_tag = item_li.find('span', class_='hot-value')
                    hot_value = hot_value_tag.get_text(strip=True) if hot_value_tag else None
                    
                    if title and url:
                        item = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            hot_value=hot_value,
                            publish_time=datetime.now()
                        )
                        items.append(item)
                        rank += 1
                except Exception as e:
                    logger.warning(f"解析什么值得买条目失败: {e}")
                    continue
            return items
        except Exception as e:
            logger.error(f"爬取什么值得买失败: {e}", exc_info=True)
            return []