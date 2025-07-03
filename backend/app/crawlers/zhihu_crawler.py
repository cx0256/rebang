"""知乎热榜爬虫"""
from typing import List
from datetime import datetime
import json
import re
import logging
logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem


class ZhihuCrawler(BaseCrawler):
    """知乎热榜爬虫"""
    
    def __init__(self):
        super().__init__("知乎", "热榜")
        self.base_url = "https://www.zhihu.com"
        self.hot_url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
        self.headers.update({
            'Referer': 'https://www.zhihu.com/',
            'Accept': 'application/json, text/plain, */*',
        })
    
    async def crawl(self) -> List[HotItem]:
        """爬取知乎热榜"""
        try:
            # 知乎热榜API
            params = {
                'limit': 50,
                'desktop': 'true'
            }
            
            # 获取热榜数据
            data = await self.fetch_json(self.hot_url, params=params)
            
            items = []
            
            if 'data' in data:
                for idx, item_data in enumerate(data['data'], 1):
                    try:
                        target = item_data.get('target', {})
                        
                        # 提取基本信息
                        title = target.get('title', '')
                        question_id = target.get('id', '')
                        url = f"https://www.zhihu.com/question/{question_id}" if question_id else ""
                        
                        # 提取热度值
                        detail_text = item_data.get('detail_text', '')
                        hot_value = detail_text.replace('万热度', '').strip() if detail_text else None
                        
                        # 提取摘要
                        excerpt = target.get('excerpt', '')
                        
                        # 提取作者信息
                        author_info = target.get('author', {})
                        author = author_info.get('name', '') if author_info else None
                        
                        # 提取回答数
                        answer_count = target.get('answer_count', 0)
                        
                        # 提取创建时间
                        created_time = target.get('created_time')
                        publish_time = None
                        if created_time:
                            try:
                                publish_time = datetime.fromtimestamp(created_time)
                            except:
                                publish_time = datetime.now()
                        
                        if title and url:
                            item = HotItem(
                                title=title,
                                url=url,
                                rank=idx,
                                hot_value=hot_value,
                                author=author,
                                comment_count=answer_count,
                                publish_time=publish_time,
                                summary=excerpt[:200] if excerpt else None
                            )
                            items.append(item)
                    
                    except Exception as e:
                        logger.warning(f"解析知乎热榜条目失败: {e}")
                        continue
            
            return items
            
        except Exception as e:
            logger.error(f"爬取知乎热榜失败: {e}")
            # 如果API失败，尝试爬取网页版
            return await self._crawl_web_version()
    
    async def _crawl_web_version(self) -> List[HotItem]:
        """爬取知乎热榜网页版（备用方案）"""
        try:
            web_url = "https://www.zhihu.com/hot"
            html = await self.fetch(web_url)
            soup = self.parse_html(html)
            
            items = []
            rank = 1
            
            # 查找热榜条目
            hot_items = soup.find_all('div', class_='HotItem')
            
            for item_div in hot_items[:50]:
                try:
                    # 提取标题和链接
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
                    
                    # 提取热度值
                    hot_div = item_div.find('div', class_='HotItem-metrics')
                    hot_value = hot_div.get_text(strip=True) if hot_div else None
                    
                    # 提取摘要
                    excerpt_div = item_div.find('div', class_='HotItem-excerpt')
                    summary = excerpt_div.get_text(strip=True) if excerpt_div else None
                    
                    if title and url:
                        item = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            hot_value=hot_value,
                            summary=summary[:200] if summary else None,
                            publish_time=datetime.now()
                        )
                        items.append(item)
                        rank += 1
                
                except Exception as e:
                    logger.warning(f"解析知乎热榜网页条目失败: {e}")
                    continue
            
            return items
            
        except Exception as e:
            logger.error(f"爬取知乎热榜网页版失败: {e}")
            return []