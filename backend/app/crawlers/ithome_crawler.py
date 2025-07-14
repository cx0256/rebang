"""IT之家热榜爬虫"""
from typing import List
from datetime import datetime
import re
import logging
logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem


class ITHomeCrawler(BaseCrawler):
    """IT之家热榜爬虫"""
    
    def __init__(self):
        super().__init__("IT之家", "热榜")
        self.base_url = "https://www.ithome.com"
        self.hot_url = "https://m.ithome.com/rankm/"
        self.headers.update({
            'Referer': 'https://www.ithome.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    async def crawl(self) -> List[HotItem]:
        """爬取IT之家热榜"""
        try:
            # 获取首页
            html = await self.fetch(self.hot_url)
            soup = self.parse_html(html)
            
            items = []
            rank = 1
            
            # 查找热门文章 - 调整为更具体的选择器
            rank_list = soup.find('ul', class_='rank')
            if rank_list:
                hot_items = rank_list.find_all('li')
            else:
                hot_items = []
            
            for item_li in hot_items[:30]:  # 取前30条
                try:
                    title_tag = item_li.find('a')
                    if not title_tag:
                        continue

                    title = title_tag.get_text(strip=True)
                    url = title_tag['href']

                    hot_value_tag = item_li.find('span', class_='hot-num')
                    hot_value = hot_value_tag.get_text(strip=True) if hot_value_tag else '0'

                    if title and url:
                        item = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            hot_value=hot_value,
                            tags=["科技"]
                        )
                        items.append(item)
                        rank += 1
                
                except Exception as e:
                    logger.warning(f"解析IT之家条目失败: {e}")
                    continue
            
            return items[:30]  # 确保返回30条
            
        except Exception as e:
            logger.error(f"爬取IT之家热榜失败: {e}")
            return []