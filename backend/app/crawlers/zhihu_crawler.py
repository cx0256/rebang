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
            # 使用知乎热榜页面
            url = "https://www.zhihu.com/hot"
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            logger.info(f"正在请求知乎热榜页面: {url}")
            
            html = await self.fetch(url, headers=headers)
            soup = self.parse_html(html)
            
            items = []
            rank = 1
            
            # 知乎可能需要登录才能看到热榜，尝试通用链接选择器
            selectors = [
                'a[href*="zhihu.com/question/"]',
                'a[href*="zhihu.com/answer/"]',
                'a[href*="zhihu.com/p/"]',
                'a[href*="/question/"]',
                'a[href*="/answer/"]',
                'a[href*="/p/"]'
            ]
            
            hot_items = []
            for selector in selectors:
                hot_items = soup.select(selector)
                if hot_items:
                    logger.info(f"使用选择器 {selector} 找到 {len(hot_items)} 个条目")
                    break
            
            if not hot_items:
                logger.warning("未找到任何热榜条目")
                return []
            
            for item in hot_items[:30]:  # 取前30条
                try:
                    # 提取标题
                    title_selectors = [
                        '.HotItem-title',
                        '.ContentItem-title',
                        'h2 a',
                        '.TopstoryItem-title',
                        'a[data-za-detail-view-element_name="Title"]',
                        '.HotList-itemTitle'
                    ]
                    
                    title = ''
                    title_link = None
                    for title_sel in title_selectors:
                        title_elem = item.select_one(title_sel)
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                            if title_elem.name == 'a':
                                title_link = title_elem
                            else:
                                title_link = title_elem.find('a')
                            break
                    
                    if not title:
                        continue
                    
                    # 提取URL
                    url_val = ''
                    if title_link and title_link.get('href'):
                        href = title_link.get('href')
                        if href.startswith('//'):
                            url_val = 'https:' + href
                        elif href.startswith('/'):
                            url_val = 'https://www.zhihu.com' + href
                        elif href.startswith('http'):
                            url_val = href
                    
                    if not url_val:
                        continue
                    
                    # 提取热度
                    hot_selectors = [
                        '.HotItem-metrics',
                        '.ContentItem-meta',
                        '.TopstoryItem-meta',
                        '.HotList-itemMetrics'
                    ]
                    
                    hot_value = '0'
                    for hot_sel in hot_selectors:
                        hot_elem = item.select_one(hot_sel)
                        if hot_elem:
                            hot_text = hot_elem.get_text(strip=True)
                            if '万' in hot_text:
                                try:
                                    import re
                                    match = re.search(r'([\d.]+)万', hot_text)
                                    if match:
                                        hot_num = float(match.group(1))
                                        hot_value = str(int(hot_num * 10000))
                                except (ValueError, AttributeError):
                                    pass
                            break
                    
                    item_obj = HotItem(
                        title=title,
                        url=url_val,
                        rank=rank,
                        hot_value=hot_value,
                        publish_time=datetime.now()
                    )
                    items.append(item_obj)
                    rank += 1
                    
                except Exception as e:
                    logger.warning(f"解析知乎热榜条目失败: {e}")
                    continue
            
            logger.info(f"成功解析到 {len(items)} 条知乎热榜")
            return items
                    
        except Exception as e:
            logger.error(f"爬取知乎热榜失败: {e}", exc_info=True)
            return []