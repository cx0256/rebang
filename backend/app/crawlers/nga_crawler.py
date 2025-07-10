"""NGA杂谈爬虫"""
from typing import List
from datetime import datetime
import re
import logging
import json
import os
import aiohttp
logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem


class NGACrawler(BaseCrawler):
    """NGA杂谈爬虫"""
    
    def __init__(self):
        super().__init__("NGA", "杂谈")
        self.base_url = "https://bbs.nga.cn"
        # 尝试使用多个可能的URL
        # 首先尝试杂谈版块，如果失败则尝试热门版块
        self.hot_urls = [
            "https://bbs.nga.cn/thread.php?fid=-7",  # 杂谈
            "https://bbs.nga.cn/thread.php?fid=7",   # 艾泽拉斯议事厅
            "https://bbs.nga.cn/thread.php?fid=323", # 炉石传说
            "https://bbs.nga.cn/thread.php?fid=414"  # 游戏综合讨论
        ]
        self.hot_url = self.hot_urls[0]
        
        # 加载保存的Cookie
        cookie_string = self._load_cookies()
        
        # 添加更真实的浏览器请求头来避免403错误
        self.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Referer': 'https://bbs.nga.cn/',
            'Cache-Control': 'max-age=0',
            'Cookie': cookie_string
        })
    
    def _load_cookies(self) -> str:
        """Load cookies from nga_cookies.json file"""
        cookie_file = 'nga_cookies.json'
        default_cookies = 'ngaPassportUid=0; ngaPassportCid=0; lastvisit=0; __ngaClientCheckThreadViewCount=1'
        
        try:
            if os.path.exists(cookie_file):
                with open(cookie_file, 'r', encoding='utf-8') as f:
                    cookies_dict = json.load(f)
                
                # Convert dict to cookie string
                cookie_parts = []
                for key, value in cookies_dict.items():
                    cookie_parts.append(f"{key}={value}")
                
                # Add default cookies if not present
                if 'lastvisit' not in cookies_dict:
                    cookie_parts.append('lastvisit=0')
                if '__ngaClientCheckThreadViewCount' not in cookies_dict:
                    cookie_parts.append('__ngaClientCheckThreadViewCount=1')
                
                cookie_string = '; '.join(cookie_parts)
                logger.info(f"Loaded cookies from {cookie_file}: {len(cookies_dict)} cookies")
                return cookie_string
            else:
                logger.warning(f"Cookie file {cookie_file} not found, using default cookies")
                return default_cookies
        except Exception as e:
            logger.error(f"Failed to load cookies from {cookie_file}: {e}")
            return default_cookies
    
    async def crawl(self) -> List[HotItem]:
        """爬取NGA杂谈热榜"""
        html = None
        soup = None
        
        # 确保session已创建
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )
        
        # 尝试多个URL，直到成功获取数据
        for url in self.hot_urls:
            try:
                logger.info(f"尝试访问NGA URL: {url}")
                html = await self.fetch(url)
                soup = self.parse_html(html)
                self.hot_url = url  # 更新成功的URL
                logger.info(f"成功访问NGA URL: {url}")
                break
            except Exception as e:
                logger.warning(f"访问 {url} 失败: {e}")
                continue
        
        if not html or not soup:
            logger.error("所有NGA URL都无法访问")
            return []
        
        try:
            
            items = []
            rank = 1
            
            # 查找帖子列表
            # NGA的帖子通常在class为"topicrow"的tr标签中
            topic_rows = soup.find_all('tr', class_='topicrow')
            
            for row in topic_rows[:30]:  # 取前30条
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
                    if href.startswith('http'):
                        url = href
                    elif href.startswith('/'):
                        url = self.base_url + href
                    elif href.startswith('thread.php') or href.startswith('read.php'):
                        url = f"{self.base_url}/{href}"
                    else:
                        # 如果是相对路径，添加基础URL
                        url = f"{self.base_url}/{href}" if href else None
                    
                    # 验证URL是否有效
                    if not url or not url.startswith('http'):
                        logger.warning(f"无效的URL: {href}")
                        continue
                    
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
            # 确保session已创建
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                )
            
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