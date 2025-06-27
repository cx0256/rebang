"""虎扑热榜爬虫"""
from typing import List
from datetime import datetime
import re
import logging
logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem


class HupuCrawler(BaseCrawler):
    """虎扑热榜爬虫"""
    
    def __init__(self):
        super().__init__("虎扑", "热榜")
        self.base_url = "https://bbs.hupu.com"
        self.hot_url = "https://bbs.hupu.com/all-gambia"
        self.headers.update({
            'Referer': 'https://bbs.hupu.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    async def crawl(self) -> List[HotItem]:
        """爬取虎扑热榜"""
        try:
            # 获取热榜页面
            html = await self.fetch(self.hot_url)
            soup = self.parse_html(html)
            
            items = []
            rank = 1
            
            # 查找热榜条目
            hot_items = soup.find_all('li', class_='bbs-sl-web-post-layout')
            
            for item_li in hot_items[:30]:  # 取前30条
                try:
                    # 提取标题和链接
                    title_link = item_li.find('a', class_='truetit')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    href = title_link.get('href', '')
                    
                    # 构建完整URL
                    if href.startswith('/'):
                        url = self.base_url + href
                    else:
                        url = href
                    
                    # 提取作者
                    author_link = item_li.find('a', class_='aulink')
                    author = author_link.get_text(strip=True) if author_link else ''
                    
                    # 提取回复数
                    reply_span = item_li.find('span', class_='ansour red')
                    comment_count = 0
                    if reply_span:
                        reply_text = reply_span.get_text(strip=True)
                        reply_match = re.search(r'(\d+)', reply_text)
                        if reply_match:
                            comment_count = int(reply_match.group(1))
                    
                    # 提取发布时间
                    time_span = item_li.find('span', class_='ansour')
                    publish_time = datetime.now()
                    if time_span:
                        time_text = time_span.get_text(strip=True)
                        # 解析时间格式，如"2小时前"、"昨天 15:30"等
                        if '小时前' in time_text:
                            hours_match = re.search(r'(\d+)小时前', time_text)
                            if hours_match:
                                hours = int(hours_match.group(1))
                                publish_time = datetime.now().replace(hour=datetime.now().hour - hours)
                        elif '分钟前' in time_text:
                            minutes_match = re.search(r'(\d+)分钟前', time_text)
                            if minutes_match:
                                minutes = int(minutes_match.group(1))
                                publish_time = datetime.now().replace(minute=datetime.now().minute - minutes)
                    
                    # 提取板块信息
                    forum_link = item_li.find('a', class_='ansour')
                    forum = forum_link.get_text(strip=True) if forum_link else ''
                    tags = [forum] if forum else None
                    
                    if title and url:
                        item = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            author=author,
                            comment_count=comment_count,
                            tags=tags,
                            publish_time=publish_time
                        )
                        items.append(item)
                        rank += 1
                
                except Exception as e:
                    logger.warning(f"解析虎扑热榜条目失败: {e}")
                    continue
            
            return items
            
        except Exception as e:
            logger.error(f"爬取虎扑热榜失败: {e}")
            return []
    
    async def get_topic_detail(self, url: str) -> dict:
        """获取帖子详情"""
        try:
            html = await self.fetch(url)
            soup = self.parse_html(html)
            
            # 提取帖子内容
            content_div = soup.find('div', class_='quote-content')
            content = content_div.get_text(strip=True) if content_div else ''
            
            # 提取图片
            images = []
            img_tags = soup.find_all('img', class_='img')
            for img in img_tags:
                src = img.get('src', '')
                if src and src.startswith('http'):
                    images.append(src)
            
            return {
                'content': content,
                'images': images
            }
            
        except Exception as e:
            logger.error(f"获取虎扑帖子详情失败: {e}")
            return {}