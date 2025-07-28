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
        """爬取B站热门视频"""
        try:
            # 先尝试API接口
            api_items = await self._crawl_api_version()
            if api_items:
                return api_items
            
            # API失败则使用网页版爬取
            web_url = "https://www.bilibili.com/v/popular/rank/all"
            html = await self.fetch(web_url)
            soup = self.parse_html(html)
            
            items = []
            rank = 1
            
            # 查找热榜条目 - 更新选择器
            hot_items = soup.find_all('div', class_='rank-item')
            if not hot_items:
                # 尝试其他可能的选择器
                hot_items = soup.find_all('li', class_='rank-item')
            if not hot_items:
                hot_items = soup.find_all('div', class_='video-card')
            
            logger.info(f"找到 {len(hot_items)} 个热榜条目")
            
            for item_div in hot_items[:30]:  # 取前30条
                try:
                    # 提取标题和链接
                    title_link = item_div.find('a', class_='title') or item_div.find('a')
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
                    author = ''
                    author_elem = item_div.find('span', class_='up-name') or item_div.find('a', class_='up-name')
                    if author_elem:
                        author = author_elem.get_text(strip=True)
                    
                    # 提取播放量
                    hot_value = ''
                    play_elem = item_div.find('span', class_='play-text') or item_div.find('div', class_='play')
                    if play_elem:
                        hot_value = play_elem.get_text(strip=True)
                    
                    # 提取图片
                    img_tag = item_div.find('img')
                    image_url = img_tag.get('src', '') if img_tag else None
                    
                    if title and url:
                        item = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            author=author,
                            hot_value=hot_value,
                            image_url=image_url,
                            publish_time=datetime.now()
                        )
                        items.append(item)
                        rank += 1
                        logger.debug(f"解析到B站视频: {title}")
                
                except Exception as e:
                    logger.warning(f"解析B站热榜条目失败: {e}")
                    continue
            
            logger.info(f"成功解析到 {len(items)} 条B站视频")
            return items
            
        except Exception as e:
            logger.error(f"爬取B站热榜失败: {e}")
            return []
    
    async def _crawl_api_version(self) -> List[HotItem]:
        """使用API接口爬取B站热榜"""
        try:
            import json
            api_url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
            response = await self.fetch(api_url)
            
            # 尝试解析JSON
            try:
                data = json.loads(response)
                if data.get('code') == 0 and data.get('data'):
                    items = []
                    rank = 1
                    
                    for video in data['data']['list'][:30]:
                        try:
                            title = video.get('title', '')
                            bvid = video.get('bvid', '')
                            url = f"https://www.bilibili.com/video/{bvid}" if bvid else ''
                            
                            # 获取UP主信息
                            owner = video.get('owner', {})
                            author = owner.get('name', '')
                            
                            # 获取统计信息
                            stat = video.get('stat', {})
                            view_count = stat.get('view', 0)
                            hot_value = f"{view_count}播放"
                            
                            # 获取封面
                            pic = video.get('pic', '')
                            
                            if title and url:
                                item = HotItem(
                                    title=title,
                                    url=url,
                                    rank=rank,
                                    author=author,
                                    hot_value=hot_value,
                                    image_url=pic,
                                    publish_time=datetime.now()
                                )
                                items.append(item)
                                rank += 1
                                logger.debug(f"解析到B站视频: {title}")
                        
                        except Exception as e:
                            logger.warning(f"解析B站API视频数据失败: {e}")
                            continue
                    
                    logger.info(f"通过API成功解析到 {len(items)} 条B站视频")
                    return items
            
            except json.JSONDecodeError:
                logger.warning("B站API返回的不是有效JSON")
                return []
                
        except Exception as e:
            logger.error(f"B站API爬取失败: {e}")
            return []
    
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