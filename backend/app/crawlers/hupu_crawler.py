"""虎扑热榜爬虫"""
from typing import List
from datetime import datetime
import re
import logging
logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem


class HupuCrawler(BaseCrawler):
    """虎扑热榜爬虫"""
    
    def __init__(self):
        super().__init__("虎扑", "热榜")
        self.base_url = "https://bbs.hupu.com"
        self.hot_url = "https://bbs.hupu.com/all-gambia"  # 虎扑步行街热榜
        self.backup_urls = [
            "https://m.hupu.com/bbs/all-gambia",  # 移动版
            "https://bbs.hupu.com/",  # 虎扑首页
            "https://m.hupu.com/",  # 移动版首页
            "https://bbs.hupu.com/all"  # 全部版块
        ]
        self.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://m.hupu.com/'
        })
    
    async def crawl(self) -> List[HotItem]:
        """爬取虎扑热榜"""
        # 首先尝试主干道API，获取多页数据以达到30条
        all_items = []
        
        # 主干道多页爬取
        for page in range(1, 4):  # 爬取前3页
            try:
                url = f'https://m.hupu.com/api/v2/bbs/topicThreads?topicId=1&page={page}'
                logger.info(f"开始爬取虎扑主干道第{page}页: {url}")
                html = await self.fetch(url)
                items = await self._parse_hupu_api(html, url, len(all_items))
                
                if items:
                    all_items.extend(items)
                    logger.info(f"第{page}页获取到 {len(items)} 条数据，累计 {len(all_items)} 条")
                    
                    # 如果已经获取到30条或更多，停止爬取
                    if len(all_items) >= 30:
                        break
                else:
                    logger.warning(f"第{page}页未获取到数据")
                    
            except Exception as e:
                logger.warning(f"爬取虎扑主干道第{page}页失败: {e}")
                continue
        
        # 如果主干道数据足够，直接返回前30条
        if len(all_items) >= 30:
            logger.info(f"成功从主干道获取到 {len(all_items[:30])} 条数据")
            return all_items[:30]
        
        # 如果主干道数据不够，尝试其他版块API
        api_urls = [
            'https://m.hupu.com/api/v2/bbs/topicThreads?topicId=6&page=1',   # 恋爱区
            'https://m.hupu.com/api/v2/bbs/topicThreads?topicId=11&page=1',  # 校园区
            'https://m.hupu.com/api/v2/bbs/topicThreads?topicId=12&page=1',  # 历史区
        ]
        
        for url in api_urls:
            if len(all_items) >= 30:
                break
                
            try:
                logger.info(f"开始爬取虎扑API: {url}")
                html = await self.fetch(url)
                items = await self._parse_hupu_api(html, url, len(all_items))
                
                if items:
                    all_items.extend(items)
                    logger.info(f"从API {url} 获取到 {len(items)} 条数据，累计 {len(all_items)} 条")
                else:
                    logger.warning(f"从API {url} 未获取到数据")
                    
            except Exception as e:
                logger.warning(f"爬取虎扑API {url} 失败: {e}")
                continue
        
        # 如果API获取到足够数据，返回前30条
        if all_items:
            logger.info(f"成功从API获取到 {len(all_items[:30])} 条数据")
            return all_items[:30]
        
        # 如果API失败，尝试HTML页面
        html_urls = [self.hot_url] + self.backup_urls
        for url in html_urls:
            try:
                logger.info(f"尝试爬取虎扑URL: {url}")
                html = await self.fetch(url)
                soup = self.parse_html(html)
                
                items = await self._parse_hupu_page(soup, url)
                if items:
                    logger.info(f"从 {url} 成功获取到 {len(items)} 条数据")
                    return items[:30]  # 返回前30条
                    
            except Exception as e:
                logger.warning(f"爬取虎扑URL {url} 失败: {e}")
                continue
        
        logger.error("所有虎扑URL都爬取失败")
        return []
    
    async def _parse_hupu_api(self, response_text: str, url: str, start_rank: int = 0) -> List[HotItem]:
        """解析虎扑API响应"""
        try:
            import json
            data = json.loads(response_text)
            
            if data.get('code') != 200:
                logger.warning(f"虎扑API返回错误: {data.get('msg', 'Unknown error')}")
                return []
            
            # 修正数据结构解析
            result_data = data.get('data', {})
            if isinstance(result_data, dict):
                threads = result_data.get('data', [])
            else:
                threads = result_data if isinstance(result_data, list) else []
            
            if not threads:
                logger.warning(f"虎扑API未返回帖子数据，响应结构: {data}")
                return []
            
            items = []
            for i, thread in enumerate(threads):  # 处理所有返回的数据
                try:
                    title = thread.get('title', '').strip()
                    tid = thread.get('tid', '')
                    author = thread.get('username', '')
                    replies = str(thread.get('replies', 0))
                    
                    if not title or not tid:
                        continue
                    
                    # 构建URL
                    url = f"https://bbs.hupu.com/{tid}.html"
                    
                    # 获取发布时间
                    publish_time = datetime.now()
                    create_time = thread.get('createTime')
                    if create_time:
                        try:
                            publish_time = datetime.fromtimestamp(int(create_time))
                        except (ValueError, TypeError):
                            pass
                    
                    item_obj = HotItem(
                        title=title,
                        url=url,
                        rank=start_rank + i + 1,  # 使用连续排名
                        author=author,
                        comment_count=replies,
                        hot_value=replies,  # 使用回复数作为热度
                        publish_time=publish_time,
                        extra_data={
                            'tid': tid,
                            'mobile_url': thread.get('url', ''),
                            'forum': thread.get('forumName', '')
                        }
                    )
                    items.append(item_obj)
                    logger.debug(f"解析到虎扑API帖子: {title}")
                    
                except Exception as e:
                    logger.warning(f"解析虎扑API帖子失败: {e}")
                    continue
            
            logger.info(f"成功从虎扑API解析到 {len(items)} 条数据")
            return items
            
        except json.JSONDecodeError as e:
            logger.error(f"解析虎扑API JSON失败: {e}")
            return []
        except Exception as e:
            logger.error(f"解析虎扑API响应失败: {e}")
            return []
    
    async def _parse_hupu_page(self, soup, url: str) -> List[HotItem]:
        """解析虎扑页面"""
        try:
            
            # 查找热榜条目 - 尝试多种选择器
            hot_items = []
            
            # 虎扑步行街的选择器（基于调试结果）
            selectors = [
                '.fufu-post-card',  # 虎扑新版页面的帖子卡片
                '[class*="post"]',  # 包含post的所有类
                '.list-item',
                '.list-item-wrap',
                '.topic-list .list-item',
                'div.list-item',
                'a[href*="/bbs/"]',
                'a[href*=".html"]'
            ]
            
            for selector in selectors:
                items = soup.select(selector)
                if items:
                    hot_items = items
                    logger.info(f"使用选择器 {selector} 找到 {len(items)} 个条目")
                    break
            
            # 如果还是没找到，尝试查找所有包含虎扑链接的元素
            if not hot_items:
                logger.info("尝试通用链接选择器...")
                all_links = soup.find_all('a', href=True)
                thread_parents = set()
                for link in all_links:
                    href = link.get('href', '')
                    if '/thread-' in href or '/post-' in href or 'tid=' in href:
                        parent = link.parent
                        while parent and parent.name not in ['li', 'tr', 'div']:
                            parent = parent.parent
                        if parent and parent not in thread_parents:
                            thread_parents.add(parent)
                            hot_items.append(parent)
                logger.info(f"通过链接查找到 {len(hot_items)} 个条目")
            
            logger.info(f"最终找到 {len(hot_items)} 个虎扑热榜条目")
            
            items = []
            rank = 1
            
            for item_elem in hot_items[:30]:  # 取前30条
                try:
                    # 提取标题和链接 - 针对新版虎扑页面结构
                    title_link = None
                    if 'fufu-post-card' in item_elem.get('class', []):
                        # 新版虎扑页面结构
                        links = item_elem.find_all('a', href=True)
                        for link in links:
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            # 选择主要的帖子链接（不包含评论链接）
                            if (href and text and len(text) > 10 and 
                                '.html' in href and 
                                '#master-discuss-section' not in href and
                                not text.isdigit()):
                                title_link = link
                                break
                    elif item_elem.name == 'tr':
                        # 表格行格式
                        title_link = item_elem.find('a', href=True)
                    else:
                        # 其他格式 - 查找所有链接并选择最合适的
                        links = item_elem.find_all('a', href=True)
                        for link in links:
                            href = link.get('href', '')
                            text = link.get_text(strip=True)
                            # 过滤掉导航链接和空链接，选择帖子链接
                            if (href and text and len(text) > 5 and 
                                not any(skip in href for skip in ['/all-', '/user/', '/login', '/register', 'javascript:', '#']) and
                                ('/thread-' in href or '/post-' in href or 'tid=' in href or '.html' in href)):
                                title_link = link
                                break
                        
                        # 如果没找到特定的帖子链接，使用第一个有效链接
                        if not title_link:
                            title_link = item_elem.find('a', class_='title') or item_elem.find('a', href=True)
                    
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    href = title_link.get('href', '')
                    
                    # 过滤无效链接
                    if not href:
                        continue
                    
                    # 构建完整URL
                    if href.startswith('//'):
                        url = 'https:' + href
                    elif href.startswith('/'):
                        url = self.base_url + href
                    else:
                        url = href
                    
                    # 提取作者
                    author = ''
                    author_elem = item_elem.find('a', class_='author') or item_elem.find('cite')
                    if author_elem:
                        author = author_elem.get_text(strip=True)
                    
                    # 提取回复数
                    comment_count = ''
                    if 'fufu-post-card' in item_elem.get('class', []):
                        # 新版虎扑页面结构 - 查找评论数链接
                        comment_links = item_elem.find_all('a', class_='comment')
                        for comment_link in comment_links:
                            comment_text = comment_link.get_text(strip=True)
                            if comment_text.isdigit():
                                comment_count = comment_text
                                break
                    else:
                        # 旧版页面结构
                        reply_elem = item_elem.find('span', class_='reply-count') or item_elem.find('em')
                        if reply_elem:
                            reply_text = reply_elem.get_text(strip=True)
                            reply_match = re.search(r'(\d+)', reply_text)
                            if reply_match:
                                comment_count = reply_match.group(1)
                    
                    # 提取发布时间
                    publish_time = datetime.now()
                    time_elem = item_elem.find('span', class_='time') or item_elem.find('em', class_='time')
                    if time_elem:
                        time_text = time_elem.get_text(strip=True)
                        # 简单处理时间
                        if '小时前' in time_text or '分钟前' in time_text or '天前' in time_text:
                            publish_time = datetime.now()
                    
                    # 提取板块信息
                    forum = ''
                    forum_elem = item_elem.find('a', class_='forum')
                    if forum_elem:
                        forum = forum_elem.get_text(strip=True)
                    
                    if title and url and len(title) > 3:  # 过滤太短的标题
                        item_obj = HotItem(
                            title=title,
                            url=url,
                            rank=rank,
                            author=author,
                            comment_count=comment_count,
                            hot_value=comment_count,  # 使用回复数作为热度
                            publish_time=publish_time,
                            extra_data={'forum': forum} if forum else None
                        )
                        items.append(item_obj)
                        rank += 1
                        logger.debug(f"解析到虎扑帖子: {title}")
                
                except Exception as e:
                    logger.warning(f"解析虎扑热榜条目失败: {e}")
                    continue
            
            logger.info(f"成功解析到 {len(items)} 条虎扑热榜数据")
            return items
            
        except Exception as e:
            logger.error(f"解析虎扑页面失败: {e}")
            return []
    
    async def get_topic_detail(self, url: str) -> dict:
        """获取帖子详情"""
        try:
            html = await self.fetch(url)
            soup = self.parse_html(html)
            
            # 提取帖子内容
            content_div = soup.find('div', class_='quote-content')
            content = content_div.get_text(strip=True) if content_div else ''
            
            # 提取图片
            images = []
            img_tags = soup.find_all('img', class_='img')
            for img in img_tags:
                src = img.get('src', '')
                if src and src.startswith('http'):
                    images.append(src)
            
            return {
                'content': content,
                'images': images
            }
            
        except Exception as e:
            logger.error(f"获取虎扑帖子详情失败: {e}")
            return {}