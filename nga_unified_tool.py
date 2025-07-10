#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NGA统一工具 - 集成所有NGA相关功能
包括Cookie管理、验证、测试、Selenium爬虫等
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional
import re

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend" / "app"))

# 检查依赖
try:
    import aiohttp
except ImportError:
    print("⚠️ aiohttp未安装，某些功能可能不可用")
    aiohttp = None

try:
    from selenium import webdriver
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# 导入项目模块
try:
    from backend.app.crawlers.nga_crawler import NGACrawler
    from backend.app.crawlers.nga_cookie_manager import NGACookieManager
except ImportError as e:
    print(f"⚠️ 导入错误: {e}")
    print("请确保项目结构正确")

class NGAUnifiedTool:
    """NGA统一工具类"""
    
    def __init__(self):
        self.config_file = "nga_cookies.json"
        self.cookie_manager = None
        self.crawler = None
        
        # 初始化Cookie管理器
        try:
            self.cookie_manager = NGACookieManager()
        except:
            print("⚠️ Cookie管理器初始化失败")
    
    def print_header(self):
        """打印工具头部信息"""
        print("\n" + "="*60)
        print("🚀 NGA统一工具 v2.0")
        print("集成Cookie管理、验证、测试、Selenium爬虫")
        print("="*60)
    
    def print_main_menu(self):
        """显示主菜单"""
        print("\n📋 主菜单:")
        print("1. 🍪 Cookie管理")
        print("2. ✅ Cookie验证")
        print("3. 🕷️ 爬虫测试")
        print("4. 🤖 Selenium功能")
        print("5. 🔧 环境检查")
        print("6. 🧪 完整测试")
        print("7. 📖 使用指南")
        print("8. 🗑️ 清理配置")
        print("0. 🚪 退出")
        print("-" * 40)
    
    def print_cookie_menu(self):
        """显示Cookie管理菜单"""
        print("\n🍪 Cookie管理:")
        print("1. 手动输入Cookie")
        print("2. 从字符串解析Cookie")
        print("3. 查看当前Cookie状态")
        print("4. 导出Cookie")
        print("5. 删除Cookie")
        print("0. 返回主菜单")
    
    def print_selenium_menu(self):
        """显示Selenium功能菜单"""
        print("\n🤖 Selenium功能:")
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium未安装")
            print("请运行: pip install selenium")
            print("0. 返回主菜单")
            return
        
        print("1. 测试Selenium环境")
        print("2. 使用Selenium登录获取Cookie")
        print("3. 使用Selenium爬取内容")
        print("4. Selenium完整测试")
        print("0. 返回主菜单")
    
    def load_cookies(self) -> Dict[str, str]:
        """加载保存的cookies"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ 加载Cookie失败: {e}")
        return {}
    
    def save_cookies(self, cookies: Dict[str, str]) -> bool:
        """保存cookies到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 保存Cookie失败: {e}")
            return False
    
    def manual_input_cookies(self):
        """手动输入Cookie"""
        print("\n📝 手动输入Cookie")
        print("请输入NGA登录所需的Cookie信息:")
        
        uid = input("ngaPassportUid: ").strip()
        cid = input("ngaPassportCid: ").strip()
        
        if not uid or not cid:
            print("❌ UID和CID不能为空")
            return
        
        cookies = {
            "ngaPassportUid": uid,
            "ngaPassportCid": cid
        }
        
        # 可选的额外Cookie
        lastvisit = input("lastvisit (可选): ").strip()
        if lastvisit:
            cookies["lastvisit"] = lastvisit
        
        if self.save_cookies(cookies):
            print("✅ Cookie保存成功")
        else:
            print("❌ Cookie保存失败")
    
    def parse_cookie_string(self):
        """从Cookie字符串解析"""
        print("\n🔍 从Cookie字符串解析")
        print("请粘贴从浏览器复制的完整Cookie字符串:")
        
        cookie_string = input().strip()
        if not cookie_string:
            print("❌ Cookie字符串不能为空")
            return
        
        # 解析Cookie字符串
        cookies = {}
        for item in cookie_string.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookies[key] = value
        
        # 提取关键Cookie
        nga_cookies = {}
        for key in ['ngaPassportUid', 'ngaPassportCid', 'lastvisit', 'lastpath']:
            if key in cookies:
                nga_cookies[key] = cookies[key]
        
        if nga_cookies:
            print(f"✅ 解析到 {len(nga_cookies)} 个有效Cookie")
            for key, value in nga_cookies.items():
                print(f"   {key}: {value[:20]}...")
            
            if self.save_cookies(nga_cookies):
                print("✅ Cookie保存成功")
            else:
                print("❌ Cookie保存失败")
        else:
            print("❌ 未找到有效的NGA Cookie")
    
    def show_cookie_status(self):
        """显示当前Cookie状态"""
        print("\n📊 当前Cookie状态")
        
        cookies = self.load_cookies()
        if not cookies:
            print("❌ 未找到保存的Cookie")
            return
        
        print(f"✅ 找到 {len(cookies)} 个Cookie:")
        for key, value in cookies.items():
            print(f"   {key}: {value[:20]}...")
        
        # 检查必需的Cookie
        required = ['ngaPassportUid', 'ngaPassportCid']
        missing = [key for key in required if key not in cookies]
        
        if missing:
            print(f"⚠️ 缺少必需的Cookie: {', '.join(missing)}")
        else:
            print("✅ 包含所有必需的Cookie")
    
    def export_cookies(self):
        """导出Cookie"""
        print("\n📤 导出Cookie")
        
        cookies = self.load_cookies()
        if not cookies:
            print("❌ 未找到保存的Cookie")
            return
        
        # 生成Cookie字符串
        cookie_string = '; '.join([f"{k}={v}" for k, v in cookies.items()])
        
        print("\n📋 Cookie字符串:")
        print(cookie_string)
        
        # 保存到文件
        try:
            with open('exported_cookies.txt', 'w', encoding='utf-8') as f:
                f.write(cookie_string)
            print("\n✅ Cookie已导出到 exported_cookies.txt")
        except Exception as e:
            print(f"❌ 导出失败: {e}")
    
    def delete_cookies(self):
        """删除Cookie"""
        print("\n🗑️ 删除Cookie")
        
        if os.path.exists(self.config_file):
            try:
                os.remove(self.config_file)
                print("✅ Cookie已删除")
            except Exception as e:
                print(f"❌ 删除失败: {e}")
        else:
            print("ℹ️ 没有找到Cookie文件")
    
    async def verify_cookies(self):
        """验证Cookie有效性"""
        print("\n✅ 验证Cookie有效性")
        
        cookies = self.load_cookies()
        if not cookies:
            print("❌ 未找到保存的Cookie")
            return False
        
        if not aiohttp:
            print("❌ aiohttp未安装，无法进行网络验证")
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                # 测试访问NGA首页
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with session.get(
                    'https://bbs.nga.cn/',
                    cookies=cookies,
                    headers=headers,
                    timeout=10
                ) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # 检查登录状态 - 更准确的方法
                        # 检查是否有用户ID和用户名信息
                        if '__CURRENT_UID' in content and '__CURRENT_UNAME' in content:
                            # 提取用户ID
                            import re
                            uid_match = re.search(r'__CURRENT_UID = parseInt\(\'(\d+)\',10\)', content)
                            uname_match = re.search(r'__CURRENT_UNAME = \'([^\']*)\',', content)
                            
                            if uid_match and uname_match and uid_match.group(1) != '0':
                                uid = uid_match.group(1)
                                uname = uname_match.group(1)
                                print(f"✅ Cookie验证成功 - 已登录状态")
                                print(f"   用户ID: {uid}")
                                print(f"   用户名: {uname}")
                                return True
                            else:
                                print("⚠️ Cookie可能已失效 - 用户ID为0或未找到用户信息")
                                return False
                        else:
                            print("⚠️ Cookie可能已失效 - 未检测到登录状态")
                            return False
                    else:
                        print(f"❌ 访问失败 - HTTP {response.status}")
                        return False
        
        except Exception as e:
            print(f"❌ 验证失败: {e}")
            return False
    
    async def test_crawler(self):
        """测试爬虫功能"""
        print("\n🕷️ 测试爬虫功能")
        
        try:
            crawler = NGACrawler()
            items = await crawler.crawl()
            
            if items:
                print(f"✅ 爬虫测试成功 - 获取到 {len(items)} 条数据")
                
                # 显示前3条
                for i, item in enumerate(items[:3], 1):
                    print(f"   {i}. {item.title[:50]}...")
                    print(f"      作者: {item.author or 'Unknown'}")
                    print(f"      链接: {item.url}")
                    print()
                return True
            else:
                print("⚠️ 爬虫测试失败 - 未获取到数据")
                return False
        
        except Exception as e:
            print(f"❌ 爬虫测试失败: {e}")
            return False
    
    async def test_selenium_environment(self):
        """测试Selenium环境"""
        print("\n🔧 测试Selenium环境")
        
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium未安装")
            return False
        
        try:
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            driver.get("https://www.baidu.com")
            title = driver.title
            driver.quit()
            
            print(f"✅ Selenium环境正常")
            print(f"   测试页面标题: {title}")
            return True
        
        except Exception as e:
            print(f"❌ Selenium环境测试失败: {e}")
            print("\n💡 解决方案:")
            print("   1. 安装ChromeDriver: https://chromedriver.chromium.org/")
            print("   2. 确保Chrome浏览器已安装")
            print("   3. 安装selenium: pip install selenium")
            return False
    
    async def selenium_login(self):
        """使用Selenium登录获取Cookie"""
        print("\n🔐 使用Selenium登录")
        
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium未安装")
            return
        
        username = input("请输入用户名: ").strip()
        password = input("请输入密码: ").strip()
        
        if not username or not password:
            print("❌ 用户名和密码不能为空")
            return
        
        try:
            from backend.app.crawlers.nga_selenium_crawler import SeleniumNGACrawler
            
            crawler = SeleniumNGACrawler(headless=False, manual_captcha=True)
            crawler.driver = crawler._setup_driver()
            
            print("\n🔄 开始登录过程...")
            print("如果出现验证码，请在浏览器中手动输入")
            print("完成后程序会自动继续")
            
            success = await crawler.login_with_selenium(username, password)
            
            if success:
                print("✅ 登录成功！")
                
                # 获取Cookie
                cookies = crawler.get_cookies_dict()
                print(f"\n📋 获取到的Cookie:")
                for key, value in cookies.items():
                    print(f"   {key}: {value[:20]}...")
                
                # 保存Cookie
                if self.save_cookies(cookies):
                    print("\n✅ Cookie已保存到配置文件")
                else:
                    print("\n❌ Cookie保存失败")
            else:
                print("❌ 登录失败")
            
            crawler.close()
        
        except Exception as e:
            print(f"❌ Selenium登录失败: {e}")
    
    async def selenium_crawl(self):
        """使用Selenium爬取内容"""
        print("\n🕷️ 使用Selenium爬取内容")
        
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium未安装")
            return
        
        try:
            from backend.app.crawlers.nga_selenium_crawler import SeleniumNGACrawler
            
            crawler = SeleniumNGACrawler(headless=True, manual_captcha=False)
            crawler.driver = crawler._setup_driver()
            
            print("🔄 开始爬取...")
            items = await crawler.crawl()
            
            if items:
                print(f"✅ 爬取成功 - 获取到 {len(items)} 条数据")
                
                # 显示前5条
                for i, item in enumerate(items[:5], 1):
                    print(f"   {i}. {item.title[:60]}...")
                    print(f"      作者: {item.author or 'Unknown'}")
                    print(f"      回复: {item.comment_count or 'N/A'}")
                    print()
            else:
                print("⚠️ 未获取到数据")
            
            crawler.close()
        
        except Exception as e:
            print(f"❌ Selenium爬取失败: {e}")
    
    def check_environment(self):
        """检查环境依赖"""
        print("\n🔧 环境检查")
        
        # 检查Python版本
        python_version = sys.version
        print(f"Python版本: {python_version.split()[0]}")
        
        # 检查依赖包
        dependencies = {
            'aiohttp': aiohttp is not None,
            'selenium': SELENIUM_AVAILABLE,
        }
        
        print("\n📦 依赖包状态:")
        for package, available in dependencies.items():
            status = "✅" if available else "❌"
            print(f"   {status} {package}")
        
        # 检查文件
        files_to_check = [
            'backend/app/crawlers/nga_crawler.py',
            'backend/app/crawlers/nga_cookie_manager.py',
            'backend/app/crawlers/nga_selenium_crawler.py'
        ]
        
        print("\n📁 文件检查:")
        for file_path in files_to_check:
            exists = os.path.exists(file_path)
            status = "✅" if exists else "❌"
            print(f"   {status} {file_path}")
        
        # 检查配置文件
        print("\n⚙️ 配置文件:")
        config_exists = os.path.exists(self.config_file)
        status = "✅" if config_exists else "⚠️"
        print(f"   {status} {self.config_file}")
        
        if config_exists:
            cookies = self.load_cookies()
            print(f"      包含 {len(cookies)} 个Cookie")
    
    async def full_test(self):
        """完整功能测试"""
        print("\n🧪 完整功能测试")
        
        results = []
        
        # 测试1: 环境检查
        print("\n--- 测试1: 环境检查 ---")
        self.check_environment()
        results.append(("环境检查", True))
        
        # 测试2: Cookie验证
        print("\n--- 测试2: Cookie验证 ---")
        cookie_valid = await self.verify_cookies()
        results.append(("Cookie验证", cookie_valid))
        
        # 测试3: 爬虫测试
        print("\n--- 测试3: 爬虫测试 ---")
        crawler_ok = await self.test_crawler()
        results.append(("爬虫测试", crawler_ok))
        
        # 测试4: Selenium环境
        if SELENIUM_AVAILABLE:
            print("\n--- 测试4: Selenium环境 ---")
            selenium_ok = await self.test_selenium_environment()
            results.append(("Selenium环境", selenium_ok))
        
        # 显示测试结果
        print("\n" + "="*50)
        print("📊 测试结果汇总")
        print("="*50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {test_name}")
            if result:
                passed += 1
        
        print(f"\n总计: {passed}/{total} 项测试通过")
        
        if passed == total:
            print("🎉 所有测试通过！系统运行正常")
        elif passed >= total * 0.8:
            print("✅ 大部分测试通过，系统基本可用")
        else:
            print("⚠️ 多项测试失败，请检查配置")
    
    def show_guide(self):
        """显示使用指南"""
        print("\n📖 使用指南")
        print("-" * 40)
        
        print("\n🍪 Cookie获取步骤:")
        print("1. 打开浏览器，访问 https://bbs.nga.cn")
        print("2. 登录你的NGA账号")
        print("3. 按F12打开开发者工具")
        print("4. 切换到Network标签")
        print("5. 刷新页面")
        print("6. 找到任意请求，查看Request Headers")
        print("7. 复制Cookie字符串")
        print("8. 在本工具中选择'从字符串解析Cookie'")
        
        print("\n🤖 Selenium使用建议:")
        print("1. 首次使用建议用Selenium登录获取Cookie")
        print("2. 日常使用HTTP爬虫+保存的Cookie")
        print("3. Cookie失效时再次使用Selenium更新")
        print("4. 遇到验证码时使用非无头模式")
        
        print("\n🔧 故障排除:")
        print("1. Cookie失效 -> 重新获取Cookie")
        print("2. 爬虫无数据 -> 检查Cookie和网络")
        print("3. Selenium失败 -> 检查ChromeDriver")
        print("4. 验证码问题 -> 使用手动模式")
        
        print("\n📚 相关文档:")
        print("- NGA_SELENIUM_GUIDE.md - Selenium详细指南")
        print("- CRAWLER_GUIDE.md - 爬虫使用指南")
    
    def clear_config(self):
        """清理配置"""
        print("\n🗑️ 清理配置")
        
        files_to_clean = [
            self.config_file,
            'exported_cookies.txt',
            'nga_test_results.json'
        ]
        
        cleaned = 0
        for file_path in files_to_clean:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"✅ 已删除: {file_path}")
                    cleaned += 1
                except Exception as e:
                    print(f"❌ 删除失败 {file_path}: {e}")
        
        if cleaned == 0:
            print("ℹ️ 没有找到需要清理的文件")
        else:
            print(f"\n✅ 清理完成，删除了 {cleaned} 个文件")
    
    async def handle_cookie_management(self):
        """处理Cookie管理"""
        while True:
            self.print_cookie_menu()
            choice = input("\n请选择操作 (0-5): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.manual_input_cookies()
            elif choice == '2':
                self.parse_cookie_string()
            elif choice == '3':
                self.show_cookie_status()
            elif choice == '4':
                self.export_cookies()
            elif choice == '5':
                self.delete_cookies()
            else:
                print("❌ 无效选择")
            
            input("\n按回车键继续...")
    
    async def handle_selenium_functions(self):
        """处理Selenium功能"""
        while True:
            self.print_selenium_menu()
            
            if not SELENIUM_AVAILABLE:
                input("\n按回车键返回主菜单...")
                break
            
            choice = input("\n请选择操作 (0-4): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                await self.test_selenium_environment()
            elif choice == '2':
                await self.selenium_login()
            elif choice == '3':
                await self.selenium_crawl()
            elif choice == '4':
                # Selenium完整测试
                print("\n🧪 Selenium完整测试")
                await self.test_selenium_environment()
                print("\n" + "-"*30)
                await self.selenium_crawl()
            else:
                print("❌ 无效选择")
            
            input("\n按回车键继续...")
    
    async def run(self):
        """运行主程序"""
        self.print_header()
        
        while True:
            self.print_main_menu()
            choice = input("\n请选择操作 (0-8): ").strip()
            
            try:
                if choice == '0':
                    print("\n👋 感谢使用NGA统一工具！")
                    break
                elif choice == '1':
                    await self.handle_cookie_management()
                elif choice == '2':
                    await self.verify_cookies()
                    input("\n按回车键继续...")
                elif choice == '3':
                    await self.test_crawler()
                    input("\n按回车键继续...")
                elif choice == '4':
                    await self.handle_selenium_functions()
                elif choice == '5':
                    self.check_environment()
                    input("\n按回车键继续...")
                elif choice == '6':
                    await self.full_test()
                    input("\n按回车键继续...")
                elif choice == '7':
                    self.show_guide()
                    input("\n按回车键继续...")
                elif choice == '8':
                    self.clear_config()
                    input("\n按回车键继续...")
                else:
                    print("❌ 无效选择，请输入0-8之间的数字")
            
            except KeyboardInterrupt:
                print("\n\n⏹️ 操作被用户中断")
                break
            except Exception as e:
                print(f"\n❌ 操作失败: {e}")
                input("\n按回车键继续...")

async def main():
    """主函数"""
    tool = NGAUnifiedTool()
    await tool.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n💥 程序崩溃: {e}")
        import traceback
        traceback.print_exc()