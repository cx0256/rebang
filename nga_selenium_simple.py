#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NGA Selenium爬虫 - 简化版示例
回答用户关于Selenium方法的问题
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend" / "app"))

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium未安装，请运行: pip install selenium")

try:
    from backend.app.crawlers.base import BaseCrawler, HotItem
except ImportError:
    print("⚠️ 无法导入BaseCrawler，使用简化版本")
    
    class BaseCrawler:
        def __init__(self, platform: str, category: str):
            self.platform = platform
            self.category = category
    
    class HotItem:
        def __init__(self, title, url, rank=None, author=None, comment_count=None, publish_time=None):
            self.title = title
            self.url = url
            self.rank = rank
            self.author = author
            self.comment_count = comment_count
            self.publish_time = publish_time

class SeleniumNGACrawler(BaseCrawler):
    """用户提出的Selenium方法的改进版本"""
    
    def __init__(self):
        super().__init__("NGA", "热榜")
        self.driver = None
    
    def setup_driver(self, headless=True):
        """设置Chrome驱动"""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium未安装，请运行: pip install selenium")
        
        options = Options()
        
        if headless:
            options.add_argument('--headless')  # 后台运行
        
        # 添加常用选项
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # 设置User-Agent
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)
            print("✅ Chrome驱动设置成功")
            return True
        except Exception as e:
            print(f"❌ Chrome驱动设置失败: {e}")
            print("💡 请确保已安装ChromeDriver并添加到PATH")
            print("   下载地址: https://chromedriver.chromium.org/")
            return False
    
    async def login_with_selenium(self, username: str, password: str, manual_captcha=True):
        """使用Selenium处理登录和验证码 - 改进版"""
        if not self.driver:
            print("❌ 驱动未初始化，请先调用setup_driver()")
            return None
        
        try:
            print("🔄 开始登录流程...")
            
            # 访问NGA登录页面
            login_url = "https://bbs.nga.cn/nuke.php?__lib=login&__act=login_page"
            self.driver.get(login_url)
            
            # 等待页面加载
            await asyncio.sleep(2)
            
            # 查找用户名输入框（NGA可能使用不同的字段名）
            username_selectors = [
                "input[name='username']",
                "input[name='uid']", 
                "input[name='email']",
                "input[id='username']"
            ]
            
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ 找到用户名输入框: {selector}")
                    break
                except:
                    continue
            
            if not username_field:
                print("❌ 未找到用户名输入框")
                return None
            
            # 查找密码输入框
            password_selectors = [
                "input[name='password']",
                "input[name='passwd']",
                "input[type='password']"
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ 找到密码输入框: {selector}")
                    break
                except:
                    continue
            
            if not password_field:
                print("❌ 未找到密码输入框")
                return None
            
            # 输入用户名和密码
            username_field.clear()
            username_field.send_keys(username)
            
            password_field.clear()
            password_field.send_keys(password)
            
            print("✅ 用户名和密码已输入")
            
            # 检查验证码
            captcha_found = False
            captcha_selectors = [
                "img[src*='captcha']",
                "img[src*='verify']", 
                "img[src*='code']",
                ".captcha img"
            ]
            
            for selector in captcha_selectors:
                try:
                    captcha_img = self.driver.find_element(By.CSS_SELECTOR, selector)
                    captcha_found = True
                    print(f"⚠️ 检测到验证码: {selector}")
                    break
                except:
                    continue
            
            # 处理验证码
            if captcha_found and manual_captcha:
                print("\n" + "="*50)
                print("🔐 检测到验证码")
                print("请在浏览器中手动输入验证码")
                print("完成后按回车键继续...")
                print("="*50)
                input()
            elif captcha_found:
                print("⚠️ 检测到验证码但未启用手动处理")
                return None
            
            # 查找并点击登录按钮
            login_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "input[value*='登录']",
                "input[value*='Login']",
                ".login-btn"
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ 找到登录按钮: {selector}")
                    break
                except:
                    continue
            
            if login_button:
                login_button.click()
                print("🔄 已点击登录按钮")
            else:
                # 尝试提交表单
                try:
                    form = self.driver.find_element(By.TAG_NAME, "form")
                    form.submit()
                    print("🔄 已提交登录表单")
                except:
                    print("❌ 未找到登录按钮或表单")
                    return None
            
            # 等待登录完成
            await asyncio.sleep(3)
            
            # 检查登录是否成功
            current_url = self.driver.current_url
            page_source = self.driver.page_source
            
            success_indicators = [
                "退出" in page_source,
                "logout" in page_source.lower(),
                "个人设置" in page_source,
                "用户中心" in page_source
            ]
            
            if any(success_indicators):
                print("✅ 登录成功！")
                
                # 获取cookies
                cookies = self.driver.get_cookies()
                nga_cookies = self._extract_nga_cookies(cookies)
                
                print(f"📋 提取到的NGA Cookies:")
                for key, value in nga_cookies.items():
                    print(f"   {key}: {value[:20]}...")
                
                return nga_cookies
            else:
                print("❌ 登录失败 - 未检测到登录成功标志")
                print(f"当前URL: {current_url}")
                return None
        
        except Exception as e:
            print(f"❌ 登录过程出错: {e}")
            return None
    
    def _extract_nga_cookies(self, selenium_cookies):
        """从Selenium cookies中提取NGA所需的关键cookie"""
        nga_cookies = {}
        
        for cookie in selenium_cookies:
            name = cookie.get('name', '')
            value = cookie.get('value', '')
            
            # 提取关键的NGA cookie
            if name in ['ngaPassportUid', 'ngaPassportCid', 'lastvisit', 'lastpath']:
                nga_cookies[name] = value
        
        return nga_cookies
    
    async def crawl_forum(self, forum_url=None):
        """爬取论坛内容"""
        if not self.driver:
            print("❌ 驱动未初始化")
            return []
        
        # 默认爬取网事杂谈
        if not forum_url:
            forum_url = "https://bbs.nga.cn/thread.php?fid=-7"
        
        try:
            print(f"🔄 开始爬取论坛: {forum_url}")
            self.driver.get(forum_url)
            await asyncio.sleep(3)
            
            items = []
            
            # 查找帖子列表
            topic_selectors = [
                "tr.topicrow",
                ".topicrow", 
                "tr[class*='topic']"
            ]
            
            topic_rows = []
            for selector in topic_selectors:
                try:
                    topic_rows = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if topic_rows:
                        print(f"✅ 找到帖子列表: {selector} ({len(topic_rows)}条)")
                        break
                except:
                    continue
            
            if not topic_rows:
                print("⚠️ 未找到帖子列表")
                return []
            
            # 解析帖子
            for i, row in enumerate(topic_rows[:20], 1):  # 限制前20条
                try:
                    # 提取标题和链接
                    title_selectors = [
                        "td.c2 a",
                        ".c2 a",
                        "td:nth-child(2) a"
                    ]
                    
                    title_element = None
                    for selector in title_selectors:
                        try:
                            title_element = row.find_element(By.CSS_SELECTOR, selector)
                            break
                        except:
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
                    try:
                        author_element = row.find_element(By.CSS_SELECTOR, "td.c3")
                        author = author_element.text.strip()
                    except:
                        pass
                    
                    # 创建HotItem
                    item = HotItem(
                        title=title,
                        url=url,
                        rank=i,
                        author=author
                    )
                    
                    items.append(item)
                    
                except Exception as e:
                    print(f"⚠️ 解析第{i}条帖子失败: {e}")
                    continue
            
            print(f"✅ 成功爬取 {len(items)} 条帖子")
            return items
        
        except Exception as e:
            print(f"❌ 爬取失败: {e}")
            return []
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ 浏览器已关闭")
            except Exception as e:
                print(f"⚠️ 关闭浏览器时出错: {e}")
            finally:
                self.driver = None
    
    def __del__(self):
        """析构函数"""
        self.close()

# 使用示例和测试
async def demo_usage():
    """演示用法"""
    print("\n" + "="*60)
    print("🚀 NGA Selenium爬虫演示")
    print("="*60)
    
    if not SELENIUM_AVAILABLE:
        print("\n❌ Selenium未安装，无法运行演示")
        print("请运行: pip install selenium")
        return
    
    crawler = SeleniumNGACrawler()
    
    try:
        # 1. 设置驱动
        print("\n--- 步骤1: 设置Chrome驱动 ---")
        if not crawler.setup_driver(headless=True):
            print("❌ 驱动设置失败，演示结束")
            return
        
        # 2. 测试论坛爬取（无需登录）
        print("\n--- 步骤2: 测试论坛爬取 ---")
        items = await crawler.crawl_forum()
        
        if items:
            print(f"\n📋 爬取结果 (前5条):")
            for item in items[:5]:
                print(f"   • {item.title[:50]}...")
                print(f"     作者: {item.author or 'Unknown'}")
                print(f"     链接: {item.url}")
                print()
        
        # 3. 登录演示（需要真实账号）
        print("\n--- 步骤3: 登录演示 ---")
        print("⚠️ 登录需要真实的NGA账号，此处仅演示流程")
        print("如需测试登录，请修改代码中的用户名和密码")
        
        # 取消注释下面的代码来测试登录
        # username = "your_username"
        # password = "your_password"
        # cookies = await crawler.login_with_selenium(username, password)
        # if cookies:
        #     print("✅ 登录成功，获取到cookies")
        # else:
        #     print("❌ 登录失败")
    
    finally:
        crawler.close()

def analyze_user_method():
    """分析用户提出的方法"""
    print("\n" + "="*60)
    print("📝 用户方法分析")
    print("="*60)
    
    print("\n✅ 用户方法的优点:")
    print("   1. 基本结构正确，继承了BaseCrawler")
    print("   2. 使用了正确的Selenium导入")
    print("   3. 设置了Chrome选项")
    print("   4. 包含了手动验证码处理")
    print("   5. 提取cookies的思路正确")
    
    print("\n⚠️ 需要改进的地方:")
    print("   1. 缺少错误处理和异常捕获")
    print("   2. 登录页面URL不够准确")
    print("   3. 元素查找方式过于简单，NGA可能使用不同的字段名")
    print("   4. 缺少登录成功的验证逻辑")
    print("   5. 没有处理页面加载等待")
    print("   6. Cookie提取方法未实现")
    
    print("\n💡 改进建议:")
    print("   1. 添加多种元素选择器以提高兼容性")
    print("   2. 使用WebDriverWait进行显式等待")
    print("   3. 添加登录成功的多种验证方式")
    print("   4. 实现完整的Cookie提取和保存逻辑")
    print("   5. 添加详细的日志和错误处理")
    print("   6. 支持无头模式和可视化模式切换")
    
    print("\n🎯 总结:")
    print("   用户的方法是一个很好的起点，基本思路正确。")
    print("   通过添加更完善的错误处理、元素查找和验证逻辑，")
    print("   可以成为一个可靠的NGA登录和爬取解决方案。")

if __name__ == "__main__":
    print("🤖 NGA Selenium爬虫 - 简化版演示")
    
    # 分析用户方法
    analyze_user_method()
    
    # 运行演示
    try:
        asyncio.run(demo_usage())
    except KeyboardInterrupt:
        print("\n⏹️ 演示被用户中断")
    except Exception as e:
        print(f"\n💥 演示出错: {e}")
        import traceback
        traceback.print_exc()