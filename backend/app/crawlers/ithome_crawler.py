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
        self.hot_url = "https://www.ithome.com/"
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
            
            # 查找热门文章
            hot_items = soup.find_all('div', class_='lst-item')
            
            for item_div in hot_items[:30]:  # 取前30条
                try:
                    # 提取标题和链接
                    title_link = item_div.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get('title', '') or title_link.get_text(strip=True)
                    href = title_link.get('href', '')
                    
                    # 构建完整URL
                    if href.startswith('/'):
                        url = self.base_url + href
                    else:
                        url = href
                    
                    # 提取摘要
                    summary_div = item_div.find('div', class_='lst-summary')
                    summary = summary_div.get_text(strip=True) if summary_div else ''
                    
                    # 提取发布时间
                    time_span = item_div.find('span', class_='time')
                    publish_time = datetime.now()
                    if time_span:
                        time_text = time_span.get_text(strip=True)
                        # 解析时间格式
                        try:
                            if '月' in time_text and '日' in time_text:
                                # 格式如"12月25日 15:30"
                                time_match = re.search(r'(\d+)月(\d+)日\s+(\d+):(\d+)', time_text)
                                if time_match:
                                    month, day, hour, minute = map(int, time_match.groups())
                                    publish_time = datetime.now().replace(
                                        month=month, day=day, hour=hour, minute=minute, second=0, microsecond=0
                                    )
                        except Exception:
                            pass
                    
                    # 提取图片
                    img_tag = item_div.find('img')
                    image_url = None
                    if img_tag:
                        src = img_tag.get('src', '') or img_tag.get('data-src', '')
                        if src and src.startswith('http'):
                            image_url = src
                        elif src and src.startswith('/'):
                            image_url = self.base_url + src
                    
                    # 提取评论数
                    comment_span = item_div.find('span', class_='comment')
                    comment_count = 0
                    if comment_span:
                        comment_text = comment_span.get_text(strip=True)
                        comment_match = re.search(r'(\d+)', comment_text)
                        if comment_match:
                            comment_count = int(comment_match.group(1))
                    
                    if title and url:
                        item = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            summary=summary,
                            comment_count=comment_count,
                            image_url=image_url,
                            publish_time=publish_time,
                            tags=["科技"]
                        )
                        items.append(item)
                        rank += 1
                
                except Exception as e:
                    logger.warning(f"解析IT之家条目失败: {e}")
                    continue
            
            # 如果主页没有足够内容，尝试获取更多
            if len(items) < 30:
                await self._crawl_more_items(items, rank)
            
            return items[:30]  # 确保返回30条
            
        except Exception as e:
            logger.error(f"爬取IT之家热榜失败: {e}")
            return []
    
    async def _crawl_more_items(self, items: List[HotItem], start_rank: int):
        """爬取更多文章"""
        try:
            # 尝试获取新闻列表页
            news_url = "https://www.ithome.com/news/"
            html = await self.fetch(news_url)
            soup = self.parse_html(html)
            
            rank = start_rank
            news_items = soup.find_all('div', class_='lst-item')
            
            for item_div in news_items:
                if len(items) >= 30:
                    break
                    
                try:
                    # 提取标题和链接
                    title_link = item_div.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get('title', '') or title_link.get_text(strip=True)
                    href = title_link.get('href', '')
                    
                    # 构建完整URL
                    if href.startswith('/'):
                        url = self.base_url + href
                    else:
                        url = href
                    
                    # 检查是否已存在
                    if any(item.url == url for item in items):
                        continue
                    
                    # 提取摘要
                    summary_div = item_div.find('div', class_='lst-summary')
                    summary = summary_div.get_text(strip=True) if summary_div else ''
                    
                    # 提取图片
                    img_tag = item_div.find('img')
                    image_url = None
                    if img_tag:
                        src = img_tag.get('src', '') or img_tag.get('data-src', '')
                        if src and src.startswith('http'):
                            image_url = src
                        elif src and src.startswith('/'):
                            image_url = self.base_url + src
                    
                    if title and url:
                        item = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            summary=summary,
                            image_url=image_url,
                            publish_time=datetime.now(),
                            tags=["科技"]
                        )
                        items.append(item)
                        rank += 1
                
                except Exception as e:
                    logger.warning(f"解析IT之家新闻条目失败: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"获取IT之家更多内容失败: {e}")