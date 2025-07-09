"""基础爬虫类"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import asyncio
import logging
logger = logging.getLogger(__name__)
from bs4 import BeautifulSoup
import json


@dataclass
class HotItem:
    """热榜条目数据类"""
    title: str
    url: str
    rank: int
    hot_value: Optional[str] = None
    author: Optional[str] = None
    comment_count: Optional[int] = None
    publish_time: Optional[datetime] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None


class BaseCrawler(ABC):
    """基础爬虫类"""
    
    def __init__(self, platform_name: str, category_name: str):
        self.platform_name = platform_name
        self.category_name = category_name
        # 为了兼容性，添加简化的属性名
        self.platform = platform_name
        self.category = category_name
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def fetch(self, url: str, max_retries: int = 3, **kwargs) -> str:
        """获取网页内容，支持重试"""
        retries = 0
        last_error = None
        
        while retries < max_retries:
            try:
                async with self.session.get(url, **kwargs) as response:
                    if response.status == 403:
                        logger.warning(f"访问被禁止 (403): {url}")
                        # 如果是403错误，可能需要更新请求头或Cookie
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message="Forbidden",
                            headers=response.headers
                        )
                    
                    response.raise_for_status()
                    return await response.text()
            except aiohttp.ClientResponseError as e:
                last_error = e
                logger.warning(f"请求失败 (尝试 {retries+1}/{max_retries}): {url}, 状态码: {e.status}")
                # 对于某些错误不重试
                if e.status in [400, 401, 403, 404]:
                    break
            except (aiohttp.ClientConnectorError, aiohttp.ServerDisconnectedError, asyncio.TimeoutError) as e:
                last_error = e
                logger.warning(f"连接错误 (尝试 {retries+1}/{max_retries}): {url}, 错误: {e}")
            except Exception as e:
                last_error = e
                logger.warning(f"未知错误 (尝试 {retries+1}/{max_retries}): {url}, 错误: {e}")
            
            retries += 1
            if retries < max_retries:
                # 指数退避重试
                await asyncio.sleep(2 ** retries)
        
        logger.error(f"获取失败 {url}: {last_error}")
        raise last_error or Exception(f"获取失败: {url}")
    
    async def fetch_json(self, url: str, **kwargs) -> Dict[str, Any]:
        """获取JSON数据"""
        try:
            async with self.session.get(url, **kwargs) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Failed to fetch JSON from {url}: {e}")
            raise
    
    @abstractmethod
    async def crawl(self) -> List[HotItem]:
        """爬取热榜数据"""
        pass
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """解析HTML"""
        return BeautifulSoup(html, 'html.parser')
    
    async def run(self) -> List[HotItem]:
        """运行爬虫"""
        logger.info(f"开始爬取 {self.platform_name} - {self.category_name}")
        try:
            async with self:
                items = await self.crawl()
                logger.info(f"成功爬取 {len(items)} 条数据")
                return items
        except Exception as e:
            logger.error(f"爬取失败: {e}")
            return []