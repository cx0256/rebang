"""B站热榜爬虫"""
from typing import List
from datetime import datetime
import re
import logging
logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem


class BiliBiliCrawler(BaseCrawler):
    """B站热榜爬虫"""
    
    def __init__(self):
        super().__init__("哔哩哔哩", "热榜")
        self.base_url = "https://www.bilibili.com"
        self.hot_url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
        self.headers.update({
            'Referer': 'https://www.bilibili.com/v/popular/rank/all',
            'Accept': 'application/json, text/plain, */*',
        })
    
    async def crawl(self) -> List[HotItem]:
        """爬取B站热榜"""
        try:
            # 获取热榜数据
            data = await self.fetch_json(self.hot_url)
            
            items = []
            
            if 'data' in data and 'list' in data['data']:
                hot_list = data['data']['list']
                
                for idx, item_data in enumerate(hot_list[:30], 1):  # 取前30条
                    try:
                        # 提取基本信息
                        title = item_data.get('title', '')
                        bvid = item_data.get('bvid', '')
                        url = f"{self.base_url}/video/{bvid}" if bvid else ""
                        
                        # 提取热度值
                        score = item_data.get('score', 0)
                        hot_value = f"{score}" if score else None
                        
                        # 提取作者
                        author = item_data.get('owner', {}).get('name', '') if item_data.get('owner') else ''
                        
                        # 提取播放量和评论数
                        play_count = item_data.get('stat', {}).get('view', 0) if item_data.get('stat') else 0
                        comment_count = item_data.get('stat', {}).get('reply', 0) if item_data.get('stat') else 0
                        
                        # 提取分区
                        tname = item_data.get('tname', '')
                        tags = [tname] if tname else None
                        
                        # 提取图片
                        image_url = item_data.get('pic', '')
                        
                        # 提取发布时间
                        pub_timestamp = item_data.get('pubdate', 0)
                        publish_time = datetime.fromtimestamp(pub_timestamp) if pub_timestamp else datetime.now()
                        
                        if title and url:
                            item = HotItem(
                                title=title,
                                url=url,
                                rank=idx,
                                hot_value=hot_value,
                                author=author,
                                comment_count=comment_count,
                                tags=tags,
                                image_url=image_url,
                                publish_time=publish_time,
                                extra_data={
                                    "play_count": play_count,
                                    "bvid": bvid
                                }
                            )
                            items.append(item)
                    
                    except Exception as e:
                        logger.warning(f"解析B站热榜条目失败: {e}")
                        continue
            
            return items
            
        except Exception as e:
            logger.error(f"爬取B站热榜失败: {e}")
            # 如果API失败，尝试爬取网页版
            return await self._crawl_web_version()
    
    async def _crawl_web_version(self) -> List[HotItem]:
        """爬取B站热榜网页版（备用方案）"""
        try:
            web_url = "https://www.bilibili.com/v/popular/rank/all"
            html = await self.fetch(web_url)
            soup = self.parse_html(html)
            
            items = []
            rank = 1
            
            # 查找热榜条目
            hot_items = soup.find_all('li', class_='rank-item')
            
            for item_li in hot_items[:30]:  # 取前30条
                try:
                    # 提取标题和链接
                    title_link = item_li.find('a', class_='title')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    href = title_link.get('href', '')
                    
                    # 构建完整URL
                    if href.startswith('//'):
                        url = "https:" + href
                    elif href.startswith('/'):
                        url = self.base_url + href
                    else:
                        url = href
                    
                    # 提取作者
                    author_div = item_li.find('div', class_='detail')
                    author = author_div.find('span', class_='data-box').get_text(strip=True) if author_div else ''
                    
                    # 提取播放量和评论数
                    play_count_span = item_li.find('span', class_='data-box')
                    play_count = play_count_span.get_text(strip=True) if play_count_span else ''
                    
                    # 提取图片
                    img_tag = item_li.find('img')
                    image_url = img_tag.get('src', '') if img_tag else None
                    
                    if title and url:
                        item = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            author=author,
                            image_url=image_url,
                            publish_time=datetime.now(),
                            extra_data={
                                "play_count": play_count
                            }
                        )
                        items.append(item)
                        rank += 1
                
                except Exception as e:
                    logger.warning(f"解析B站热榜网页条目失败: {e}")
                    continue
            
            return items
            
        except Exception as e:
            logger.error(f"爬取B站热榜网页版失败: {e}")
            return []