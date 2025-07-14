"""知乎热榜爬虫"""
from typing import List
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem

class ZhihuCrawler(BaseCrawler):
    """知乎热榜爬虫"""
    
    def __init__(self):
        super().__init__("知乎", "热榜")
        self.hot_url = "https://www.zhihu.com/hot"
    
    async def crawl(self) -> List[HotItem]:
        """爬取知乎热榜"""
        try:
            # 使用知乎API接口
            api_url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
            
            # 设置API请求的headers
            api_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://www.zhihu.com/hot',
                'Origin': 'https://www.zhihu.com'
            }
            
            # API请求参数
            params = {
                'limit': 50,
                'desktop': 'true'
            }
            
            logger.info(f"正在请求知乎API: {api_url}")
            
            html = await self.fetch(api_url, headers=api_headers, params=params)
            import json
            result = json.loads(html)
            logger.info("成功获取知乎API数据")
            
            items = []
            rank = 1
            
            # 解析API返回的数据
            if 'data' in result:
                hot_list = result['data']
                
                for item_data in hot_list[:30]:  # 取前30条
                    try:
                        target = item_data.get('target', {})
                        
                        # 提取标题
                        title = target.get('title', '').strip()
                        if not title:
                            continue
                        
                        # 构建URL
                        question_id = target.get('id')
                        if question_id:
                            url = f"https://www.zhihu.com/question/{question_id}"
                        else:
                            continue
                        
                        # 提取热度
                        detail_text = item_data.get('detail_text', '')
                        hot_value = '0'
                        if detail_text and '万热度' in detail_text:
                            try:
                                hot_num = float(detail_text.split(' ')[0])
                                hot_value = str(int(hot_num * 10000))
                            except (ValueError, IndexError):
                                hot_value = '0'
                        
                        # 提取发布时间
                        publish_time = None
                        created_time = target.get('created')
                        if created_time:
                            try:
                                publish_time = datetime.fromtimestamp(created_time)
                            except (ValueError, TypeError):
                                publish_time = datetime.now()
                        else:
                            publish_time = datetime.now()
                        
                        item = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            hot_value=hot_value,
                            publish_time=publish_time
                        )
                        items.append(item)
                        rank += 1
                        
                    except Exception as e:
                        logger.warning(f"解析知乎热榜数据失败: {e}")
                        continue
            
            logger.info(f"成功解析到 {len(items)} 条知乎热榜")
            return items
                    
        except Exception as e:
            logger.error(f"爬取知乎热榜失败: {e}", exc_info=True)
            return []