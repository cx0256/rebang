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
        self.hot_url = "https://www.zhihu.com/billboard"
    
    async def crawl(self) -> List[HotItem]:
        """爬取知乎热榜"""
        try:
            # 使用知乎热榜页面
            url = self.hot_url
            
            # 设置请求头
            # 注意：需要在此处填入有效的知乎 Cookie 才能成功获取热榜数据
            # 获取 Cookie 的方法：
            # 1. 在浏览器中登录知乎
            # 2. 打开开发者工具 (F12)
            # 3. 切换到“网络”或“Network”选项卡
            # 4. 刷新热榜页面 (https://www.zhihu.com/billboard)
            # 5. 在请求列表中找到一个对 `billboard` 的请求
            # 6. 在请求详情的“标头”或“Headers”部分，找到“请求标头”或“Request Headers”
            # 7. 复制其中 `cookie` 字段的完整值
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cookie': ' _zap=5e0b9971-61ab-4d1a-836c-1ad17720c9d2; d_c0=AGAS2nqQ8hiPTs3vpldM-gAjWV-pyKOg2MQ=|1721375080; __snaker__id=SLLts6z3aMXjddi5; _xsrf=2lRSMNMVCtkCy6C1M5ftkhSrPy8vGl58; edu_user_uuid=edu-v1|0553e654-a003-4a00-86d6-db5196abe2a4; q_c1=cf012fc87ef344ad903f36a3870135ca|1752475641000|1752475641000; __zse_ck=004_OD3xbq0EgGvxp4=IeaJn=bNNchi7LFeaR=eUzS2V8ZnEwfrHbm28RxNBl6v4N1Zhq8fynTJqx6ANkVnANnPS3i3B6U3vsQ3YDPOPnJIFxPgFMO=65MXW6QkMk8ibT2Zx-Exm5eBFIDCRNxuW1GXmm7Z3Z1AVO8ScSEdzMI1WQ+PTn4UZ1TirLB+5kuTGX/EumfZ7gxmFhUc/86Ncv0F2ezUEPcjvrFtpj4YGznpSeqMLcF58gQG4EAyZtyCL8S2zr; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1753249459,1753318090,1753436774,1753663425; HMACCOUNT=A1D9D48836E48C1F; SESSIONID=hP6p89Kh3liR6Z41cRAEWb444Hwh4LtevgO7reVAnjb; JOID=Wl0WBks6joTyEij7aTe7VsJw6dF6X9i0hyIctgcB7-umIXrCXmSjAJcXI_tqedQ3hTMUzGmU6b_ijbfvRaovges=; osd=WlsTA086iIH3Fij9bDK_VsR17NV6Wd2xgyIaswIF7-2jJH7CWGGmBJcRJv5uedIygDcUymyR7b_kiLLrRawqhO8=; tst=h; DATE=1752477569810; cmci9xde=U2FsdGVkX1+PjzDOxkkp46Ay4JmUtKTFD8ljIJwAyT6txR8lQNWhX2MGkr8lpWHSTTlHzzWTReSxybhzx9YJBA==; pmck9xge=U2FsdGVkX19IJ3bNNIageowlvPhPnmNq3fbtTjoBC3s=; crystal=U2FsdGVkX1+VizDEPdc2bNLjMqBOPMUJkiTf6IzNGOXsj6CKVrFQW6hEHMDtW7FZGKXEzhUjVPHf5Ml3vgeZyVyQWQfCE0592LgJXzWduCr2RLGgAIf9G6ZcpDvdcI0IkbvXHy4xal5I8s6eAcsjYfC2/q6JgXXWK6/8RFAY8NWgP7ZeHG+JcX/Twui0wRzefhQVMHVPXhyXXHUU+2gY5ng2yOvE83jD4Cba+wyaGq+PFddsEHPovf5mQ3poLL1m; vmce9xdq=U2FsdGVkX19BDGxeZzpdfgq71J9ZGl4uLx8U1rAvFwhD/7tvSIOQ8IPUfj1kY86uHCCBgkAZ4fFmXvL6RmvDkqR9geKeIyapaMLadLlavATy/cVUnpO13TwqxWoNO3HLEMd4lTGBr8Gw97dd0YNAHcnu6rdVAUvQmhRup29RobU=; assva6=U2FsdGVkX1+xiLPAOK2rPWnCYs9qhZJNP12Zqo0tDd4=; assva5=U2FsdGVkX1+QJQvkQB0dnnN27BFbDJTsHLfUlGmOuerdTyr5JHaHTW1ZLphipmCHsSNcoZDr8faOzvK3lp3H7w==; gdxidpyhxdE=hGHzr6HzzbeEvx57i3S%2BSz%2Bv6Xm6uwqzHhla4I%2BEsx8XgDyYW%2B5TkYdIuBM76ce7aJ1uzd1memBLOViQwmxbm5v7kBPkcE8HL1I6236EPT4K7%5CMaP9t2Pdt7gIRYftmccoWmDp2w9T754r%5CkXt2HPoYRmLqj6D1jHwCXlkwn%2FqIawMaz%3A1753690360408; captcha_session_v2=2|1:0|10:1753689462|18:captcha_session_v2|88:TGd6OGU1aFVJZWxzNWplOGNiVGhpNFZpcUU2WWpjTXV3NnRMc1NGQzdKckFNZlpjS0VkckJNeFBkVHdxT2xWVw==|c3f05bd9055939bb1a526f1eec4d10439a395e9f6145b66c80aab26a5cba2dce; captcha_ticket_v2=2|1:0|10:1753689469|17:captcha_ticket_v2|728:eyJ2YWxpZGF0ZSI6IkNOMzFfT2ZXVVo1MkVfNWJWcXZvTGFibmx0RXQqQmFYS1pJZ0FDc3BOS21DUzBibWk2WVVrQlBkY0lZZGNyRVlyMXpZZE5ES0lta1J1Z1hsU0lmYVBpbGJxakZoUklHckNHeTZCV2U1RWNBUU5xck41TnhpbEkqWnpCNlZpQkZmZDk0WFNPaEUyaDZRSldMR1IwMndMYUZKaHVpdGlDMFVxaFVfRXB0ZUplVkRGSmdYNjA0MWZ5TmIzak10SzMqclB3YUtHaklhd0dmQldnd3pRR0g2bjI0bjlsb19Eby5ZOGRWZW9RKm0wUkVZRVFBcF9RejNDNlpfbC5yWm5DdkU4cXZLQ0xLU3RLWFFwdkZqcGJkckNwNVNOUFBhc3ZQUDkzMXloMmJUZG1JWFRfd19GQ0FENmh5aEV3azJtVm8ySlppQk1kb0JJUXVLRmhFVllibGJkakJ4NHZCUHNtaHR0VUJFckltRTlMdmRkdklaaWVTZ0NLUWxueDRBQU8yVmdzMHhiM0QybWcuc0pWNlJBQ0V1dm5sQkdUMVR1OC5WWFV4TUtzM2FDWi5ubS5UTHFjclNUU0drQypzWmtNMipOT3RLZDBUUVl2VkJqX1k5Ljk5REFFKmRQMjk0T1hPaUZGOWxkZ1ZkZ0pTRm4zUVZwTmJDajFFOE1DdDk1ZmNYdzRZSkhHLmNndlk3N192X2lfMSJ9|c4348829abc1d240a4e99b428b8b0abb1b52c9029ade7d53a6545118ac639f5d; z_c0=2|1:0|10:1753689469|4:z_c0|92:Mi4xY0RRVUFBQUFBQUFBWUJMYWVwRHlHQ1lBQUFCZ0FsVk5mWHQwYVFDLWd1WThqOE85V2VvTDJGY2t0Q0pjR21TdjdB|c62d105fcea1cb8a08d137579846e90bdc58a13fc0e19573bdd3a7d99d498ee0; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1753689627; BEC=8ce9e721fafad59a55ed220f1ad7f253' # <-- 在这里填入你的知乎 Cookie
            }
            
            logger.info(f"正在请求知乎热榜页面: {url}")
            
            html = await self.fetch(url, headers=headers)
            soup = self.parse_html(html)

            script_tag = soup.find('script', id='js-initialData')
            if not script_tag:
                logger.warning("未找到ID为 'js-initialData' 的 script 标签")
                return []

            try:
                import json
                json_data = json.loads(script_tag.string)
                hot_list = json_data.get('initialState', {}).get('topstory', {}).get('hotList', [])
            except (json.JSONDecodeError, AttributeError) as e:
                logger.error(f"解析知乎热榜JSON数据失败: {e}")
                return []

            items = []
            for i, item_data in enumerate(hot_list):
                try:
                    target = item_data.get('target', {})
                    title = target.get('titleArea', {}).get('text', '')
                    link = target.get('link', {}).get('url', '')
                    metrics = target.get('metricsArea', {}).get('text', '')
                    
                    if not title or not link:
                        continue

                    hot_value = '0'
                    if '万' in metrics:
                        try:
                            import re
                            match = re.search(r'([\d.]+)万', metrics)
                            if match:
                                hot_num = float(match.group(1))
                                hot_value = str(int(hot_num * 10000))
                        except (ValueError, AttributeError):
                            pass
                    else:
                        hot_value = ''.join(filter(str.isdigit, metrics))


                    item_obj = HotItem(
                        title=title,
                        url=link,
                        rank=i + 1,
                        hot_value=hot_value,
                        publish_time=datetime.now()
                    )
                    items.append(item_obj)
                except Exception as e:
                    logger.warning(f"解析知乎热榜条目失败: {e}, item_data: {item_data}")
                    continue
            
            logger.info(f"成功解析到 {len(items)} 条知乎热榜")
            return items
                    
        except Exception as e:
            logger.error(f"爬取知乎热榜失败: {e}", exc_info=True)
            return []