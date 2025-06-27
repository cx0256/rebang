"""今日头条热榜爬虫"""
from typing import List
from datetime import datetime
import re
import logging
logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem


class ToutiaoCrawler(BaseCrawler):
    """今日头条热榜爬虫"""
    
    def __init__(self):
        super().__init__("今日头条", "热榜")
        self.base_url = "https://www.toutiao.com"
        self.hot_url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
        self.headers.update({
            'Referer': 'https://www.toutiao.com/',
            'Accept': 'application/json, text/plain, */*',
        })
    
    async def crawl(self) -> List[HotItem]:
        """爬取今日头条热榜"""
        try:
            # 获取热榜数据
            data = await self.fetch_json(self.hot_url)
            
            items = []
            
            if 'data' in data:
                hot_list = data['data']
                
                for idx, item_data in enumerate(hot_list[:30], 1):  # 取前30条
                    try:
                        # 提取基本信息
                        title = item_data.get('Title', '')
                        url = item_data.get('Url', '')
                        
                        # 构建完整URL
                        if url and not url.startswith('http'):
                            url = self.base_url + url
                        
                        # 提取热度值
                        hot_value = item_data.get('HotValue', '')
                        if not hot_value:
                            hot_value = item_data.get('hot_value', '')
                        
                        # 提取标签
                        label = item_data.get('Label', '')
                        tags = [label] if label else None
                        
                        # 提取图片
                        image_url = item_data.get('Image', {}).get('url', '') if item_data.get('Image') else ''
                        
                        if title and url:
                            item = HotItem(
                                title=title,
                                url=url,
                                rank=idx,
                                hot_value=str(hot_value) if hot_value else None,
                                tags=tags,
                                image_url=image_url if image_url else None,
                                publish_time=datetime.now()
                            )
                            items.append(item)
                    
                    except Exception as e:
                        logger.warning(f"解析今日头条热榜条目失败: {e}")
                        continue
            
            return items
            
        except Exception as e:
            logger.error(f"爬取今日头条热榜失败: {e}")
            # 如果API失败，尝试爬取网页版
            return await self._crawl_web_version()
    
    async def _crawl_web_version(self) -> List[HotItem]:
        """爬取今日头条网页版（备用方案）"""
        try:
            web_url = "https://www.toutiao.com/"
            html = await self.fetch(web_url)
            soup = self.parse_html(html)
            
            items = []
            rank = 1
            
            # 查找热榜条目（根据实际页面结构调整选择器）
            hot_items = soup.find_all('div', class_='feed-card-article')
            
            for item_div in hot_items[:30]:  # 取前30条
                try:
                    # 提取标题和链接
                    title_link = item_div.find('a', class_='title')
                    if not title_link:
                        title_link = item_div.find('a')
                    
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    href = title_link.get('href', '')
                    
                    # 构建完整URL
                    if href.startswith('/'):
                        url = self.base_url + href
                    else:
                        url = href
                    
                    # 提取图片
                    img_tag = item_div.find('img')
                    image_url = img_tag.get('src', '') if img_tag else None
                    
                    if title and url:
                        item = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            image_url=image_url,
                            publish_time=datetime.now()
                        )
                        items.append(item)
                        rank += 1
                
                except Exception as e:
                    logger.warning(f"解析今日头条网页条目失败: {e}")
                    continue
            
            return items
            
        except Exception as e:
            logger.error(f"爬取今日头条网页版失败: {e}")
            return []