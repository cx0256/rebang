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
            # 使用B站API接口
            api_url = "https://api.bilibili.com/x/web-interface/ranking/v2"
            
            # 设置API请求参数
            params = {
                'rid': 0,  # 全站排行
                'type': 1,  # 日排行
                'ps': 30   # 每页数量
            }
            
            # 设置API请求的headers
            api_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://www.bilibili.com/',
                'Origin': 'https://www.bilibili.com'
            }
            
            logger.info(f"正在请求B站API: {api_url}")
            
            # 获取热榜数据
            data = await self.fetch_json(api_url, params=params, headers=api_headers)
            
            items = []
            
            # 解析API返回的数据
            if data.get('code') == 0 and 'data' in data and 'list' in data['data']:
                video_list = data['data']['list']
                
                for rank, video_data in enumerate(video_list[:30], 1):
                    try:
                        # 提取标题
                        title = video_data.get('title', '').strip()
                        if not title:
                            continue
                        
                        # 构建URL
                        bvid = video_data.get('bvid')
                        aid = video_data.get('aid')
                        if bvid:
                            url = f"https://www.bilibili.com/video/{bvid}"
                        elif aid:
                            url = f"https://www.bilibili.com/video/av{aid}"
                        else:
                            continue
                        
                        # 提取UP主信息
                        owner = video_data.get('owner', {})
                        author = owner.get('name', '') if owner else ''
                        
                        # 提取统计信息
                        stat = video_data.get('stat', {})
                        view_count = stat.get('view', 0) if stat else 0
                        danmaku_count = stat.get('danmaku', 0) if stat else 0
                        
                        # 提取发布时间
                        publish_time = None
                        pubdate = video_data.get('pubdate')
                        if pubdate:
                            try:
                                publish_time = datetime.fromtimestamp(pubdate)
                            except (ValueError, TypeError):
                                publish_time = datetime.now()
                        else:
                            publish_time = datetime.now()
                        
                        # 提取描述
                        description = video_data.get('desc', '')
                        
                        item = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            hot_value=str(view_count),
                            author=author,
                            comment_count=str(danmaku_count),
                            description=description[:200] if description else None,  # 限制描述长度
                            publish_time=publish_time
                        )
                        items.append(item)
                        
                    except Exception as e:
                        logger.warning(f"解析B站视频数据失败: {e}")
                        continue
            
            logger.info(f"成功解析到 {len(items)} 条B站视频")
            return items
            
        except Exception as e:
            logger.error(f"B站API请求异常: {e}")
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