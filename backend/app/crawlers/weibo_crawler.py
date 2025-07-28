"""微博热搜爬虫"""
from typing import List
from datetime import datetime
import re
import logging
logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem


class WeiboCrawler(BaseCrawler):
    """微博热搜爬虫"""
    
    def __init__(self):
        super().__init__("微博", "hot")
        self.base_url = "https://weibo.com"
        self.hot_url = "https://weibo.com/ajax/side/hotSearch"
        self.headers.update({
            'Referer': 'https://weibo.com/',
            'Accept': 'application/json, text/plain, */*',
        })
    
    async def crawl(self) -> List[HotItem]:
        """爬取微博热搜"""
        try:
            # 获取热搜数据
            data = await self.fetch_json(self.hot_url)
            
            items = []
            
            if 'data' in data and 'realtime' in data['data']:
                hot_list = data['data']['realtime']
                
                for idx, item_data in enumerate(hot_list[:30], 1):  # 取前30条
                    try:
                        # 提取基本信息
                        word = item_data.get('word', '')
                        note = item_data.get('note', '')
                        title = f"{word} {note}".strip()
                        
                        # 构建搜索URL - 使用word_scheme或word
                        word_scheme = item_data.get('word_scheme')
                        if word_scheme:
                            key = word_scheme
                        else:
                            key = f"#{word}" if word else ""
                        
                        url = f"https://s.weibo.com/weibo?q={key}&t=31&band_rank=1&Refer=top" if key else ""
                        
                        # 提取热度值
                        num = item_data.get('num', 0)
                        hot_value = f"{num}" if num else None
                        
                        # 提取分类标签 - 使用flag_desc
                        flag_desc = item_data.get('flag_desc', '')
                        tags = [flag_desc] if flag_desc else None
                        
                        # 提取发布时间
                        publish_time = None
                        onboard_time = item_data.get('onboard_time')
                        if onboard_time:
                            try:
                                publish_time = datetime.fromtimestamp(onboard_time)
                            except (ValueError, TypeError):
                                publish_time = datetime.now()
                        else:
                            publish_time = datetime.now()
                        
                        if title and url:
                            item = HotItem(
                                title=title,
                                url=url,
                                rank=idx,
                                hot_value=hot_value,
                                tags=tags,
                                publish_time=publish_time
                            )
                            items.append(item)
                    
                    except Exception as e:
                        logger.warning(f"解析微博热搜条目失败: {e}")
                        continue
            
            return items
            
        except Exception as e:
            logger.error(f"爬取微博热搜失败: {e}")
            # 如果API失败，尝试爬取网页版
            return await self._crawl_web_version()
    
    async def _crawl_web_version(self) -> List[HotItem]:
        """爬取微博热搜网页版（备用方案）"""
        try:
            web_url = "https://s.weibo.com/top/summary"
            html = await self.fetch(web_url)
            soup = self.parse_html(html)
            
            items = []
            rank = 1
            
            # 查找热搜条目
            hot_items = soup.find_all('tr', class_='list-item')
            
            for item_tr in hot_items[:30]:  # 取前30条
                try:
                    # 提取标题和链接
                    title_link = item_tr.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    href = title_link.get('href', '')
                    
                    # 构建完整URL
                    if href.startswith('/'):
                        url = self.base_url + href
                    else:
                        url = href
                    
                    # 提取热度值
                    hot_span = item_tr.find('span', class_='hot')
                    hot_value = hot_span.get_text(strip=True) if hot_span else None
                    
                    # 提取标签
                    icon_span = item_tr.find('span', class_='icon')
                    tags = [icon_span.get_text(strip=True)] if icon_span else None
                    
                    if title and url:
                        item = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            hot_value=hot_value,
                            tags=tags,
                            publish_time=datetime.now()
                        )
                        items.append(item)
                        rank += 1
                
                except Exception as e:
                    logger.warning(f"解析微博热搜网页条目失败: {e}")
                    continue
            
            return items
            
        except Exception as e:
            logger.error(f"爬取微博热搜网页版失败: {e}")
            return []