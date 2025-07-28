"""IT之家热榜爬虫"""
from typing import List
from datetime import datetime
import re
import logging
logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem


class ITHomeCrawler(BaseCrawler):
    """IT之家热榜爬虫"""
    
    def __init__(self):
        super().__init__("IT之家", "热榜")
        self.base_url = "https://www.ithome.com"
        self.hot_url = "https://m.ithome.com/rankm/"
        self.backup_urls = [
            "https://www.ithome.com/",  # IT之家首页
            "https://www.ithome.com/news/",  # 新闻页面
            "https://www.ithome.com/tag/remen/"  # 热门标签页面
        ]
        self.headers.update({
            'Referer': 'https://www.ithome.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
        })
    
    async def crawl(self) -> List[HotItem]:
        """爬取IT之家热榜"""
        # 尝试多个URL
        urls_to_try = [self.hot_url] + self.backup_urls
        
        for url in urls_to_try:
            try:
                logger.info(f"尝试爬取IT之家URL: {url}")
                html = await self.fetch(url)
                soup = self.parse_html(html)
                
                items = await self._parse_ithome_page(soup, url)
                if items:
                    logger.info(f"从 {url} 成功获取到 {len(items)} 条数据")
                    return items
                    
            except Exception as e:
                logger.warning(f"爬取IT之家URL {url} 失败: {e}")
                continue
        
        logger.error("所有IT之家URL都爬取失败")
        return []
    
    async def _parse_ithome_page(self, soup, url: str) -> List[HotItem]:
        """解析IT之家页面"""
        try:
            
            # 查找热门文章 - 尝试多种选择器
            hot_items = []
            result_items = []
            rank = 1
            
            # IT之家新闻选择器
            selectors = [
                'a[href*=".htm"]',  # IT之家的新闻链接都是.htm结尾
                '.news-item a',
                '.post-item a',
                '.list-item a'
            ]
            
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    hot_items = items
                    logger.info(f"使用选择器 {selector} 找到 {len(items)} 个条目")
                    break
            
            # 如果还是没找到，尝试查找所有包含IT之家文章链接的元素
            if not hot_items:
                logger.info("尝试通用链接选择器...")
                all_links = soup.find_all('a', href=True)
                article_parents = set()
                for link in all_links:
                    href = link.get('href', '')
                    if '/news/' in href or '/post/' in href or 'newsid=' in href:
                        parent = link.parent
                        while parent and parent.name not in ['li', 'div', 'article']:
                            parent = parent.parent
                        if parent and parent not in article_parents:
                            article_parents.add(parent)
                            hot_items.append(parent)
                logger.info(f"通过链接查找到 {len(hot_items)} 个条目")
            
            logger.info(f"最终找到 {len(hot_items)} 个IT之家热榜条目")
            
            for item_elem in hot_items[:30]:  # 取前30条
                try:
                    # 如果item_elem本身就是链接
                    if item_elem.name == 'a':
                        title_tag = item_elem
                        container = item_elem.parent
                    else:
                        # 提取标题和链接
                        title_tag = item_elem.find('a', href=True)
                        container = item_elem
                        if not title_tag:
                            continue

                    # 提取完整文本（包含标题、时间、评论数）
                    full_text = title_tag.get_text(strip=True)
                    item_url = title_tag.get('href', '')
                    
                    # 过滤无效链接 - 更宽松的过滤条件
                    if not item_url or not ('.htm' in item_url and ('ithome.com' in item_url or item_url.startswith('/'))):
                        continue
                    
                    # 确保URL是完整的
                    if item_url.startswith('//'):
                        item_url = 'https:' + item_url
                    elif item_url.startswith('/'):
                        item_url = self.base_url + item_url

                    # 解析完整文本：格式通常是 "数字+标题+时间+评论数"
                    # 提取评论数 - 更精确的匹配
                    hot_value = ''
                    comment_match = re.search(r'(\d+)评$', full_text)
                    if comment_match:
                        hot_value = f"{comment_match.group(1)}评论"
                    
                    # 提取时间信息 - 更精确的匹配
                    publish_time = datetime.now()
                    time_patterns = [
                        r'(\d+小时前)',
                        r'(\d+分钟前)', 
                        r'(\d+天前)',
                        r'(昨日 \d{2}:\d{2})',
                        r'(今日 \d{2}:\d{2})',
                        r'(\d{2}-\d{2} \d{2}:\d{2})'
                    ]
                    
                    time_text = ''
                    for pattern in time_patterns:
                        time_match = re.search(pattern, full_text)
                        if time_match:
                            time_text = time_match.group(1)
                            try:
                                from datetime import timedelta
                                if '小时前' in time_text:
                                    hours = int(re.search(r'(\d+)', time_text).group(1))
                                    publish_time = datetime.now() - timedelta(hours=hours)
                                elif '分钟前' in time_text:
                                    minutes = int(re.search(r'(\d+)', time_text).group(1))
                                    publish_time = datetime.now() - timedelta(minutes=minutes)
                                elif '天前' in time_text:
                                    days = int(re.search(r'(\d+)', time_text).group(1))
                                    publish_time = datetime.now() - timedelta(days=days)
                            except:
                                pass
                            break
                    
                    # 清理标题：使用更精确的正则表达式
                    title = full_text
                    
                    # 移除开头的排名数字
                    title = re.sub(r'^\d+', '', title)
                    
                    # 移除时间信息（精确匹配）
                    if time_text:
                        title = title.replace(time_text, '')
                    
                    # 移除评论信息（精确匹配）
                    if comment_match:
                        title = title.replace(comment_match.group(0), '')
                    
                    # 移除可能残留的数字（在时间和评论之间的数字）
                    title = re.sub(r'\d+评$', '', title)
                    
                    # 清理多余的空格和特殊字符
                    title = re.sub(r'\s+', ' ', title).strip()

                    if title and item_url and len(title) > 5:  # 过滤太短的标题
                        item_obj = HotItem(
                            title=title,
                            url=item_url,
                            rank=rank,
                            hot_value=hot_value,
                            publish_time=publish_time,
                            extra_data={'category': '科技'}
                        )
                        result_items.append(item_obj)
                        rank += 1
                        logger.debug(f"解析到IT之家文章: {title}")
                
                except Exception as e:
                    logger.warning(f"解析IT之家条目失败: {e}")
                    continue
            
            logger.info(f"成功解析到 {len(result_items)} 条IT之家热榜数据")
            return result_items
            
        except Exception as e:
            logger.error(f"解析IT之家页面失败: {e}")
            return []