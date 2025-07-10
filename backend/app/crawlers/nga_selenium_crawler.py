#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NGA Selenium爬虫 - 解决验证码和登录问题
使用Selenium自动化浏览器来处理复杂的登录流程
"""

import asyncio
import logging
import time
from typing import List, Dict, Optional
from datetime import datetime
import re

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    webdriver = None
    print("Warning: Selenium not installed. Install with: pip install selenium")

from .base import BaseCrawler, HotItem

logger = logging.getLogger(__name__)

class SeleniumNGACrawler(BaseCrawler):
    """基于Selenium的NGA爬虫，支持自动登录和验证码处理"""
    
    def __init__(self, headless: bool = True, manual_captcha: bool = True):
        super().__init__("NGA", "热榜")
        
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required for this crawler. Install with: pip install selenium")
        
        self.headless = headless
        self.manual_captcha = manual_captcha
        self.driver = None
        self.logged_in = False
        
        # NGA相关配置
        self.login_url = "https://bbs.nga.cn/nuke.php?__lib=login&__act=login_page"
        self.forum_urls = [
            "https://bbs.nga.cn/thread.php?fid=-7",  # 网事杂谈
            "https://bbs.nga.cn/thread.php?fid=7",   # 艾泽拉斯议事厅
            "https://bbs.nga.cn/thread.php?fid=323", # 炉石传说
            "https://bbs.nga.cn/thread.php?fid=414"  # 游戏综合讨论
        ]
    
    def _setup_driver(self):
        """设置Chrome驱动"""
        options = Options()
        
        if self.headless:
            options.add_argument('--headless')
        
        # 添加常用选项
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36')
        
        # 禁用图片加载以提高速度（可选）
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # options.add_experimental_option("prefs", prefs)
        
        if not SELENIUM_AVAILABLE or not webdriver:
            raise ImportError("Selenium is not available")
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(10)
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            logger.info("Please make sure ChromeDriver is installed and in PATH")
            logger.info("Download from: https://chromedriver.chromium.org/")
            raise
    
    async def login_with_selenium(self, username: str, password: str) -> bool:
        """使用Selenium处理登录和验证码"""
        if not self.driver:
            self.driver = self._setup_driver()
        
        try:
            logger.info("Starting NGA login process...")
            
            # 访问登录页面
            self.driver.get(self.login_url)
            await asyncio.sleep(2)
            
            # 等待页面加载
            wait = WebDriverWait(self.driver, 10)
            
            # 查找用户名输入框（NGA可能使用不同的字段名）
            username_selectors = [
                "input[name='username']",
                "input[name='uid']",
                "input[name='email']",
                "input[id='username']",
                "input[id='uid']"
            ]
            
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not username_field:
                logger.error("Could not find username field")
                return False
            
            # 查找密码输入框
            password_selectors = [
                "input[name='password']",
                "input[name='passwd']",
                "input[id='password']",
                "input[type='password']"
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not password_field:
                logger.error("Could not find password field")
                return False
            
            # 输入用户名和密码
            username_field.clear()
            username_field.send_keys(username)
            await asyncio.sleep(0.5)
            
            password_field.clear()
            password_field.send_keys(password)
            await asyncio.sleep(0.5)
            
            # 检查是否有验证码
            captcha_img = None
            captcha_selectors = [
                "img[src*='captcha']",
                "img[src*='verify']",
                "img[src*='code']",
                ".captcha img",
                "#captcha img"
            ]
            
            for selector in captcha_selectors:
                try:
                    captcha_img = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if captcha_img:
                logger.info("Captcha detected")
                
                if self.manual_captcha:
                    if not self.headless:
                        print("\n" + "="*50)
                        print("🔐 检测到验证码")
                        print("请在浏览器中手动输入验证码")
                        print("完成后按回车键继续...")
                        print("="*50)
                        input()
                    else:
                        logger.warning("Captcha detected but running in headless mode")
                        logger.info("Consider running with headless=False for manual captcha solving")
                        return False
                else:
                    # 这里可以集成OCR服务来自动识别验证码
                    logger.warning("Automatic captcha solving not implemented")
                    return False
            
            # 查找并点击登录按钮
            login_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "input[value*='登录']",
                "input[value*='Login']",
                "button:contains('登录')",
                ".login-btn",
                "#login-btn"
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if login_button:
                login_button.click()
                await asyncio.sleep(3)
            else:
                # 尝试提交表单
                try:
                    form = self.driver.find_element(By.TAG_NAME, "form")
                    form.submit()
                    await asyncio.sleep(3)
                except NoSuchElementException:
                    logger.error("Could not find login button or form")
                    return False
            
            # 检查登录是否成功
            current_url = self.driver.current_url
            page_source = self.driver.page_source
            
            # 检查登录成功的标志
            success_indicators = [
                "退出" in page_source,
                "logout" in page_source.lower(),
                "个人设置" in page_source,
                "用户中心" in page_source,
                "ngaPassportUid" in self.driver.get_cookies().__str__()
            ]
            
            if any(success_indicators):
                logger.info("Login successful!")
                self.logged_in = True
                return True
            else:
                logger.error("Login failed - no success indicators found")
                logger.debug(f"Current URL: {current_url}")
                return False
                
        except Exception as e:
            logger.error(f"Login process failed: {e}")
            return False
    
    def _extract_nga_cookies(self, selenium_cookies: List[Dict]) -> Dict[str, str]:
        """从Selenium cookies中提取NGA所需的关键cookie"""
        nga_cookies = {}
        
        for cookie in selenium_cookies:
            name = cookie.get('name', '')
            value = cookie.get('value', '')
            
            # 提取关键的NGA cookie
            if name in ['ngaPassportUid', 'ngaPassportCid', 'lastvisit', 'lastpath']:
                nga_cookies[name] = value
        
        return nga_cookies
    
    def get_cookies_dict(self) -> Dict[str, str]:
        """获取当前浏览器的cookies"""
        if not self.driver:
            return {}
        
        selenium_cookies = self.driver.get_cookies()
        return self._extract_nga_cookies(selenium_cookies)
    
    async def crawl_with_selenium(self, target_url: str = None) -> List[HotItem]:
        """使用Selenium爬取NGA内容"""
        if not self.driver:
            logger.error("Driver not initialized")
            return []
        
        if not self.logged_in:
            logger.warning("Not logged in, some content may not be accessible")
        
        target_url = target_url or self.forum_urls[0]
        
        try:
            logger.info(f"Crawling NGA forum: {target_url}")
            self.driver.get(target_url)
            await asyncio.sleep(3)
            
            # 等待页面加载
            wait = WebDriverWait(self.driver, 10)
            
            items = []
            rank = 1
            
            # 查找帖子列表
            topic_selectors = [
                "tr.topicrow",
                ".topicrow",
                "tr[class*='topic']",
                "tr[class*='row']"
            ]
            
            topic_rows = []
            for selector in topic_selectors:
                try:
                    topic_rows = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if topic_rows:
                        break
                except NoSuchElementException:
                    continue
            
            if not topic_rows:
                logger.warning("No topic rows found")
                return []
            
            logger.info(f"Found {len(topic_rows)} topic rows")
            
            for row in topic_rows[:30]:  # 限制前30条
                try:
                    # 提取标题和链接
                    title_element = None
                    title_selectors = [
                        "td.c2 a",
                        ".c2 a",
                        "td:nth-child(2) a",
                        "a[href*='read.php']",
                        "a[href*='thread.php']"
                    ]
                    
                    for selector in title_selectors:
                        try:
                            title_element = row.find_element(By.CSS_SELECTOR, selector)
                            break
                        except NoSuchElementException:
                            continue
                    
                    if not title_element:
                        continue
                    
                    title = title_element.text.strip()
                    href = title_element.get_attribute('href')
                    
                    if not title or not href:
                        continue
                    
                    # 构建完整URL
                    if href.startswith('http'):
                        url = href
                    elif href.startswith('/'):
                        url = "https://bbs.nga.cn" + href
                    else:
                        url = "https://bbs.nga.cn/" + href
                    
                    # 提取作者
                    author = None
                    author_selectors = [
                        "td.c3",
                        ".c3",
                        "td:nth-child(3)"
                    ]
                    
                    for selector in author_selectors:
                        try:
                            author_element = row.find_element(By.CSS_SELECTOR, selector)
                            author = author_element.text.strip()
                            break
                        except NoSuchElementException:
                            continue
                    
                    # 提取回复数
                    comment_count = None
                    reply_selectors = [
                        "td.c4",
                        ".c4",
                        "td:nth-child(4)"
                    ]
                    
                    for selector in reply_selectors:
                        try:
                            reply_element = row.find_element(By.CSS_SELECTOR, selector)
                            reply_text = reply_element.text.strip()
                            reply_match = re.search(r'(\d+)', reply_text)
                            if reply_match:
                                comment_count = int(reply_match.group(1))
                            break
                        except (NoSuchElementException, ValueError):
                            continue
                    
                    # 创建HotItem
                    item = HotItem(
                        title=title,
                        url=url,
                        rank=rank,
                        author=author,
                        comment_count=comment_count,
                        publish_time=datetime.now()
                    )
                    
                    items.append(item)
                    rank += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to parse topic row: {e}")
                    continue
            
            logger.info(f"Successfully crawled {len(items)} items")
            return items
            
        except Exception as e:
            logger.error(f"Crawling failed: {e}")
            return []
    
    async def crawl(self) -> List[HotItem]:
        """实现基类的crawl方法"""
        if not self.driver:
            logger.error("Driver not initialized. Call setup_driver() first.")
            return []
        
        # 尝试多个论坛URL
        for url in self.forum_urls:
            try:
                items = await self.crawl_with_selenium(url)
                if items:
                    return items
            except Exception as e:
                logger.warning(f"Failed to crawl {url}: {e}")
                continue
        
        return []
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error closing driver: {e}")
            finally:
                self.driver = None
                self.logged_in = False
    
    def __del__(self):
        """析构函数，确保浏览器被关闭"""
        self.close()

# 使用示例
async def example_usage():
    """使用示例"""
    crawler = SeleniumNGACrawler(headless=False, manual_captcha=True)
    
    try:
        # 设置驱动
        crawler.driver = crawler._setup_driver()
        
        # 登录（如果需要）
        login_success = await crawler.login_with_selenium(
            username="15049985561",
            password="71xiaoerduo71"
        )
        
        if login_success:
            print("Login successful!")
            
            # 获取cookies
            cookies = crawler.get_cookies_dict()
            print(f"Extracted cookies: {cookies}")
        
        # 爬取内容
        items = await crawler.crawl()
        
        print(f"Crawled {len(items)} items:")
        for item in items[:5]:
            print(f"- {item.title}")
            print(f"  Author: {item.author}")
            print(f"  URL: {item.url}")
            print()
    
    finally:
        crawler.close()

if __name__ == "__main__":
    asyncio.run(example_usage())