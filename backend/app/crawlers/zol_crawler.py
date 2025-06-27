"""中关村在线热榜爬虫"""
from typing import List
from datetime import datetime
import re
import logging
logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem


class ZOLCrawler(BaseCrawler):
    """中关村在线热榜爬虫"""
    
    def __init__(self):
        super().__init__("中关村在线", "热榜")
        self.base_url = "https://www.zol.com.cn"
        self.hot_url = "https://www.zol.com.cn/"
        self.headers.update({
            'Referer': 'https://www.zol.com.cn/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    async def crawl(self) -> List[HotItem]:
        """爬取中关村在线热榜"""
        try:
            # 获取首页
            html = await self.fetch(self.hot_url)
            soup = self.parse_html(html)
            
            items = []
            rank = 1
            
            # 查找热门文章 - 多种选择器
            selectors = [
                'div.article-item',
                'li.article-item', 
                'div.news-item',
                'li.news-item',
                'div.list-item',
                'li.list-item'
            ]
            
            hot_items = []
            for selector in selectors:
                items_found = soup.select(selector)
                if items_found:
                    hot_items = items_found
                    break
            
            # 如果没找到，尝试通用选择器
            if not hot_items:
                hot_items = soup.find_all('div', class_=re.compile(r'.*item.*'))
            
            for item_div in hot_items[:30]:  # 取前30条
                try:
                    # 提取标题和链接
                    title_link = item_div.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get('title', '') or title_link.get_text(strip=True)
                    href = title_link.get('href', '')
                    
                    # 过滤无效链接
                    if not href or href == '#' or 'javascript:' in href:
                        continue
                    
                    # 构建完整URL
                    if href.startswith('//'):
                        url = 'https:' + href
                    elif href.startswith('/'):
                        url = self.base_url + href
                    elif not href.startswith('http'):
                        url = self.base_url + '/' + href
                    else:
                        url = href
                    
                    # 提取摘要
                    summary = ''
                    summary_selectors = ['.summary', '.desc', '.content', '.intro']
                    for sel in summary_selectors:
                        summary_elem = item_div.select_one(sel)
                        if summary_elem:
                            summary = summary_elem.get_text(strip=True)
                            break
                    
                    # 提取图片
                    img_tag = item_div.find('img')
                    image_url = None
                    if img_tag:
                        src = img_tag.get('src', '') or img_tag.get('data-src', '') or img_tag.get('data-original', '')
                        if src:
                            if src.startswith('//'):
                                image_url = 'https:' + src
                            elif src.startswith('/'):
                                image_url = self.base_url + src
                            elif src.startswith('http'):
                                image_url = src
                    
                    # 提取发布时间
                    publish_time = datetime.now()
                    time_selectors = ['.time', '.date', '.publish-time', '.update-time']
                    for sel in time_selectors:
                        time_elem = item_div.select_one(sel)
                        if time_elem:
                            time_text = time_elem.get_text(strip=True)
                            try:
                                # 解析各种时间格式
                                if '月' in time_text and '日' in time_text:
                                    time_match = re.search(r'(\d+)月(\d+)日', time_text)
                                    if time_match:
                                        month, day = map(int, time_match.groups())
                                        publish_time = datetime.now().replace(month=month, day=day)
                                elif '小时前' in time_text:
                                    hours_match = re.search(r'(\d+)小时前', time_text)
                                    if hours_match:
                                        hours = int(hours_match.group(1))
                                        publish_time = datetime.now().replace(hour=max(0, datetime.now().hour - hours))
                            except Exception:
                                pass
                            break
                    
                    # 提取评论数
                    comment_count = 0
                    comment_selectors = ['.comment', '.reply', '.discuss']
                    for sel in comment_selectors:
                        comment_elem = item_div.select_one(sel)
                        if comment_elem:
                            comment_text = comment_elem.get_text(strip=True)
                            comment_match = re.search(r'(\d+)', comment_text)
                            if comment_match:
                                comment_count = int(comment_match.group(1))
                            break
                    
                    if title and url and len(title) > 5:  # 确保标题有意义
                        item = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            summary=summary if summary else None,
                            comment_count=comment_count,
                            image_url=image_url,
                            publish_time=publish_time,
                            tags=["科技", "数码"]
                        )
                        items.append(item)
                        rank += 1
                
                except Exception as e:
                    logger.warning(f"解析中关村在线条目失败: {e}")
                    continue
            
            # 如果首页内容不够，尝试获取新闻页面
            if len(items) < 30:
                await self._crawl_news_page(items, rank)
            
            return items[:30]  # 确保返回30条
            
        except Exception as e:
            logger.error(f"爬取中关村在线热榜失败: {e}")
            return []
    
    async def _crawl_news_page(self, items: List[HotItem], start_rank: int):
        """爬取新闻页面获取更多内容"""
        try:
            news_url = "https://news.zol.com.cn/"
            html = await self.fetch(news_url)
            soup = self.parse_html(html)
            
            rank = start_rank
            
            # 查找新闻条目
            news_items = soup.find_all('li', class_=re.compile(r'.*item.*'))
            if not news_items:
                news_items = soup.find_all('div', class_=re.compile(r'.*item.*'))
            
            for item_elem in news_items:
                if len(items) >= 30:
                    break
                    
                try:
                    # 提取标题和链接
                    title_link = item_elem.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get('title', '') or title_link.get_text(strip=True)
                    href = title_link.get('href', '')
                    
                    if not href or href == '#':
                        continue
                    
                    # 构建完整URL
                    if href.startswith('//'):
                        url = 'https:' + href
                    elif href.startswith('/'):
                        url = self.base_url + href
                    elif not href.startswith('http'):
                        url = self.base_url + '/' + href
                    else:
                        url = href
                    
                    # 检查是否已存在
                    if any(item.url == url for item in items):
                        continue
                    
                    # 提取图片
                    img_tag = item_elem.find('img')
                    image_url = None
                    if img_tag:
                        src = img_tag.get('src', '') or img_tag.get('data-src', '')
                        if src:
                            if src.startswith('//'):
                                image_url = 'https:' + src
                            elif src.startswith('/'):
                                image_url = self.base_url + src
                            elif src.startswith('http'):
                                image_url = src
                    
                    if title and url and len(title) > 5:
                        item = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            image_url=image_url,
                            publish_time=datetime.now(),
                            tags=["科技", "数码"]
                        )
                        items.append(item)
                        rank += 1
                
                except Exception as e:
                    logger.warning(f"解析中关村在线新闻条目失败: {e}")
                    continue
                    
        except Exception as e:
            logger.warning(f"获取中关村在线新闻页面失败: {e}")