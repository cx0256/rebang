"""36氪爬虫"""
from typing import List
from datetime import datetime
import logging
import aiohttp

logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem

class Kr36Crawler(BaseCrawler):
    """36氪热榜爬虫"""
    
    def __init__(self):
        super().__init__("36氪", "热榜")
        self.api_url = "https://gateway.36kr.com/api/mis/nav/home/nav/rank/hot"
        self.headers.update({
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://m.36kr.com/',
            'Origin': 'https://m.36kr.com'
        })
    
    async def crawl(self) -> List[HotItem]:
        """爬取36氪热榜"""
        # 确保session已创建
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )
        
        try:
            # 构建请求体
            request_body = {
                "partner_id": "wap",
                "param": {
                    "siteId": 1,
                    "platformId": 2
                },
                "timestamp": int(datetime.now().timestamp() * 1000)
            }
            
            logger.info(f"正在请求36氪API: {self.api_url}")
            
            async with self.session.post(self.api_url, json=request_body) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("成功获取36氪API数据")
                    
                    items = []
                    
                    # 解析API返回的数据
                    if result.get('code') == 0 and 'data' in result and 'hotRankList' in result['data']:
                        hot_list = result['data']['hotRankList']
                        
                        for rank, item_data in enumerate(hot_list[:30], 1):
                            try:
                                # 提取模板材料
                                template_material = item_data.get('templateMaterial', {})
                                if not template_material:
                                    continue
                                
                                # 提取标题
                                title = template_material.get('widgetTitle', '').strip()
                                if not title:
                                    continue
                                
                                # 构建URL
                                item_id = item_data.get('itemId')
                                if not item_id:
                                    continue
                                
                                url = f"https://www.36kr.com/p/{item_id}"
                                
                                # 提取作者
                                author = template_material.get('authorName', '')
                                
                                # 提取封面图片
                                cover = template_material.get('widgetImage', '')
                                
                                # 提取热度
                                hot_value = str(template_material.get('statCollect', 0))
                                
                                # 提取发布时间
                                publish_time = None
                                publish_timestamp = item_data.get('publishTime')
                                if publish_timestamp:
                                    try:
                                        # 36kr的时间戳是毫秒级
                                        publish_time = datetime.fromtimestamp(publish_timestamp / 1000)
                                    except (ValueError, TypeError):
                                        publish_time = datetime.now()
                                else:
                                    publish_time = datetime.now()
                                
                                item = HotItem(
                                    title=title,
                                    url=url,
                                    rank=rank,
                                    hot_value=hot_value,
                                    author=author,
                                    image_url=cover if cover else None,
                                    publish_time=publish_time
                                )
                                items.append(item)
                                
                            except Exception as e:
                                logger.warning(f"解析36氪热榜数据失败: {e}")
                                continue
                    
                    logger.info(f"成功解析到 {len(items)} 条36氪热榜")
                    return items
                    
                else:
                    logger.error(f"36氪API请求失败，状态码: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"36氪API请求异常: {e}")
            return []