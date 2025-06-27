"""NGA杂谈爬虫"""
from typing import List
from datetime import datetime
import re
import logging
logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem


class NGACrawler(BaseCrawler):
    """NGA杂谈爬虫"""
    
    def __init__(self):
        super().__init__("NGA", "杂谈")
        self.base_url = "https://bbs.nga.cn"
        self.hot_url = "https://bbs.nga.cn/thread.php?fid=6"
    
    async def crawl(self) -> List[HotItem]:
        """爬取NGA杂谈热榜"""
        try:
            # 获取页面内容
            html = await self.fetch(self.hot_url)
            soup = self.parse_html(html)
            
            items = []
            rank = 1
            
            # 查找帖子列表
            # NGA的帖子通常在class为"topicrow"的tr标签中
            topic_rows = soup.find_all('tr', class_='topicrow')
            
            for row in topic_rows[:50]:  # 取前50条
                try:
                    # 提取标题和链接
                    title_cell = row.find('td', class_='c2')
                    if not title_cell:
                        continue
                    
                    title_link = title_cell.find('a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    href = title_link.get('href', '')
                    
                    # 构建完整URL
                    if href.startswith('/'):
                        url = self.base_url + href
                    elif href.startswith('thread.php'):
                        url = f"{self.base_url}/{href}"
                    else:
                        url = href
                    
                    # 提取作者信息
                    author_cell = row.find('td', class_='c3')
                    author = author_cell.get_text(strip=True) if author_cell else None
                    
                    # 提取回复数
                    reply_cell = row.find('td', class_='c4')
                    comment_count = None
                    if reply_cell:
                        reply_text = reply_cell.get_text(strip=True)
                        reply_match = re.search(r'(\d+)', reply_text)
                        if reply_match:
                            comment_count = int(reply_match.group(1))
                    
                    # 提取最后回复时间
                    time_cell = row.find('td', class_='c5')
                    publish_time = None
                    if time_cell:
                        time_text = time_cell.get_text(strip=True)
                        # 这里可以根据NGA的时间格式进行解析
                        # 暂时跳过时间解析，使用当前时间
                        publish_time = datetime.now()
                    
                    if title and url:
                        item = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            author=author,
                            comment_count=comment_count,
                            publish_time=publish_time
                        )
                        items.append(item)
                        rank += 1
                
                except Exception as e:
                    logger.warning(f"解析NGA帖子失败: {e}")
                    continue
            
            return items
            
        except Exception as e:
            logger.error(f"爬取NGA杂谈失败: {e}")
            return []
    
    async def get_topic_detail(self, topic_url: str) -> dict:
        """获取帖子详情"""
        try:
            html = await self.fetch(topic_url)
            soup = self.parse_html(html)
            
            # 提取帖子内容
            content_div = soup.find('div', class_='postcontent')
            content = content_div.get_text(strip=True) if content_div else ""
            
            return {
                'content': content[:500],  # 限制长度
                'summary': content[:200] if content else ""
            }
        except Exception as e:
            logger.error(f"获取NGA帖子详情失败: {e}")
            return {'content': '', 'summary': ''}