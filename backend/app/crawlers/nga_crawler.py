"""NGA杂谈爬虫"""
from typing import List
from datetime import datetime
import logging
import aiohttp
logger = logging.getLogger(__name__)

from .base import BaseCrawler, HotItem


class NGACrawler(BaseCrawler):
    """NGA杂谈爬虫"""
    
    def __init__(self):
        super().__init__("nga", "zatan")
        self.base_url = "https://bbs.nga.cn"
        
        # Set headers for API requests
        self.headers.update({
            'Accept': '*/*',
            'Host': 'ngabbs.com',
            'Referer': 'https://ngabbs.com/',
            'Connection': 'keep-alive',
            'Content-Length': '11',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-Hans-CN;q=1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'X-User-Agent': 'NGA_skull/7.3.1(iPhone13,2;iOS 17.2.1)'
        })
    
    async def crawl(self) -> List[HotItem]:
        """Crawl NGA hot topics using new API"""
        # Ensure session is created
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=30)
            )
        
        try:
            # Use new NGA API endpoint
            api_url = "https://ngabbs.com/nuke.php?__lib=load_topic&__act=load_topic_reply_ladder2&opt=1&all=1"
            
            # API request body
            data = {
                '__output': '14'
            }
            
            async with self.session.post(api_url, headers=self.headers, data=data) as response:
                if response.status == 200:
                    # Handle different content types
                    content_type = response.headers.get('content-type', '')
                    
                    if 'json' in content_type:
                        # Force JSON parsing even with non-standard content type
                        text = await response.text()
                        import json
                        result = json.loads(text)
                    else:
                        result = await response.json()
                    
                    items = []
                    rank = 1
                    topics = []
                    
                    # Parse API response data
                    if 'result' in result:
                        if len(result['result']) > 0:
                            # Check if result is a list of lists or direct list
                            if isinstance(result['result'][0], list):
                                topics = result['result'][0]  # Get first result array
                            else:
                                topics = result['result']  # Direct list
                        else:
                            logger.warning("No results found in API response")
                            return []
                    else:
                        logger.warning("Unexpected API response structure")
                        return []
                    for topic_data in topics[:30]:  # Take first 30 items
                            try:
                                # Extract title
                                title = topic_data.get('subject', '').strip()
                                if not title:
                                    continue
                                
                                # Build topic URL
                                tpcurl = topic_data.get('tpcurl')
                                if tpcurl:
                                    url = f"https://bbs.nga.cn{tpcurl}"
                                else:
                                    continue
                                
                                # Extract author
                                author = topic_data.get('author', '')
                                
                                # Extract reply count
                                comment_count = topic_data.get('replies', 0)
                                if isinstance(comment_count, str):
                                    try:
                                        comment_count = int(comment_count)
                                    except ValueError:
                                        comment_count = 0
                                
                                # Extract publish time
                                publish_time = None
                                postdate = topic_data.get('postdate')
                                if postdate:
                                    try:
                                        # NGA timestamp is usually in seconds
                                        publish_time = datetime.fromtimestamp(int(postdate))
                                    except (ValueError, TypeError):
                                        publish_time = datetime.now()
                                else:
                                    publish_time = datetime.now()
                                
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
                                logger.warning(f"Failed to parse NGA topic data: {e}")
                                continue
                    
                    return items
                    
                else:
                    logger.error(f"NGA API request failed, status code: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"NGA API request exception: {e}")
            return []
    

    
    async def get_topic_detail(self, topic_url: str) -> dict:
        """Get topic details"""
        try:
            # Ensure session is created
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                )
            
            html = await self.fetch(topic_url)
            soup = self.parse_html(html)
            
            # Extract topic content
            content_div = soup.find('div', class_='postcontent')
            content = content_div.get_text(strip=True) if content_div else ""
            
            return {
                'content': content[:500],  # Limit length
                'summary': content[:200] if content else ""
            }
        except Exception as e:
            logger.error(f"Failed to get NGA topic details: {e}")
            return {'content': '', 'summary': ''}
