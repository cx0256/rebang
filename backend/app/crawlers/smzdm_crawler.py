"""什么值得买爬虫"""
from typing import List
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem

class SmzdmCrawler(BaseCrawler):
    """什么值得买爬虫"""
    
    def __init__(self):
        super().__init__("smzdm", "hot")
        self.hot_url = "https://m.smzdm.com/top/"  # 使用移动版避免验证码
    
    async def crawl(self) -> List[HotItem]:
        """爬取什么值得买好价榜"""
        try:
            html = await self.fetch(self.hot_url)
            soup = self.parse_html(html)
            items = []
            rank = 1
            
            # 移动版页面结构不同，尝试多种选择器
            hot_items = soup.find_all('div', class_='feed-row-wide')
            if not hot_items:
                hot_items = soup.find_all('li', class_='feed-row-wide')
            if not hot_items:
                hot_items = soup.find_all('div', class_='item')
            if not hot_items:
                # 尝试通用的文章链接
                hot_items = soup.find_all('a', href=True)
                hot_items = [item for item in hot_items if '/p/' in item.get('href', '')]
            
            logger.info(f"找到 {len(hot_items)} 个什么值得买条目")
            
            # 如果找到的条目少于30个，尝试其他选择器
            if len(hot_items) < 30:
                logger.info("尝试查找更多条目...")
                # 尝试更通用的选择器
                additional_items = soup.find_all('div', class_='feed-row')
                if additional_items:
                    hot_items.extend(additional_items)
                    logger.info(f"添加了 {len(additional_items)} 个额外条目")
                
                # 尝试查找所有包含链接的div和li
                all_elements = soup.find_all(['div', 'li', 'article'])
                for elem in all_elements:
                    link = elem.find('a', href=True)
                    if link and ('/p/' in link.get('href', '') or '/post/' in link.get('href', '')) and elem not in hot_items:
                        hot_items.append(elem)
                        if len(hot_items) >= 60:  # 增加搜索范围
                            break
                
                # 如果还是不够，尝试直接查找所有链接
                if len(hot_items) < 30:
                    all_links = soup.find_all('a', href=True)
                    for link in all_links:
                        href = link.get('href', '')
                        if ('/p/' in href or '/post/' in href) and link.parent not in hot_items:
                            hot_items.append(link.parent)
                            if len(hot_items) >= 60:
                                break
                
                logger.info(f"最终找到 {len(hot_items)} 个什么值得买条目")
            
            for item in hot_items[:30]:
                try:
                    # 提取标题和链接
                    if item.name == 'a':
                        title_tag = item
                        url = item.get('href', '')
                    else:
                        title_tag = item.find('a', href=True)
                        if not title_tag:
                            continue
                        url = title_tag.get('href', '')
                    
                    title = title_tag.get_text(strip=True)
                    
                    # 确保URL是完整的
                    if url.startswith('//'):
                        url = 'https:' + url
                    elif url.startswith('/'):
                        url = 'https://www.smzdm.com' + url
                    
                    # 提取热度值
                    hot_value = ''
                    hot_value_elem = item.find('span', class_='z-highlight') or item.find('em', class_='z-highlight')
                    if hot_value_elem:
                        hot_value = hot_value_elem.get_text(strip=True)
                    
                    # 提取价格信息
                    price_elem = item.find('span', class_='z-price') or item.find('em', class_='z-price')
                    price = price_elem.get_text(strip=True) if price_elem else ''
                    
                    if title and url and len(title) > 5:  # 过滤太短的标题
                        item_obj = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            hot_value=hot_value or price,
                            publish_time=datetime.now()
                        )
                        items.append(item_obj)
                        rank += 1
                        logger.debug(f"解析到什么值得买商品: {title}")
                        
                except Exception as e:
                    logger.warning(f"解析什么值得买条目失败: {e}")
                    continue
            
            logger.info(f"成功解析到 {len(items)} 条什么值得买数据")
            return items
            
        except Exception as e:
            logger.error(f"爬取什么值得买失败: {e}", exc_info=True)
            return []