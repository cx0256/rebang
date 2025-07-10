#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NGA Selenium爬虫测试脚本
测试基于Selenium的NGA爬虫功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend" / "app"))

try:
    from backend.app.crawlers.nga_selenium_crawler import SeleniumNGACrawler
except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure the project structure is correct")
    sys.exit(1)

def print_separator(title: str):
    """打印分隔线"""
    print("\n" + "="*60)
    print(f" {title} ")
    print("="*60)

def print_subsection(title: str):
    """打印子标题"""
    print(f"\n--- {title} ---")

async def test_selenium_setup():
    """测试Selenium环境设置"""
    print_subsection("Testing Selenium Setup")
    
    try:
        # 测试无头模式
        crawler = SeleniumNGACrawler(headless=True, manual_captcha=False)
        crawler.driver = crawler._setup_driver()
        
        # 简单测试
        crawler.driver.get("https://www.baidu.com")
        title = crawler.driver.title
        print(f"✅ Selenium setup successful")
        print(f"   Test page title: {title}")
        
        crawler.close()
        return True
        
    except Exception as e:
        print(f"❌ Selenium setup failed: {e}")
        print("\n💡 Solutions:")
        print("   1. Install ChromeDriver: https://chromedriver.chromium.org/")
        print("   2. Make sure Chrome browser is installed")
        print("   3. Install selenium: pip install selenium")
        return False

async def test_nga_access():
    """测试NGA网站访问"""
    print_subsection("Testing NGA Access")
    
    try:
        crawler = SeleniumNGACrawler(headless=True, manual_captcha=False)
        crawler.driver = crawler._setup_driver()
        
        # 访问NGA首页
        crawler.driver.get("https://bbs.nga.cn")
        await asyncio.sleep(3)
        
        title = crawler.driver.title
        current_url = crawler.driver.current_url
        
        print(f"✅ NGA access successful")
        print(f"   Page title: {title}")
        print(f"   Current URL: {current_url}")
        
        # 检查页面内容
        page_source = crawler.driver.page_source
        if "nga" in page_source.lower() or "艾泽拉斯" in page_source:
            print(f"   ✅ Page content looks correct")
        else:
            print(f"   ⚠️ Page content may not be NGA")
        
        crawler.close()
        return True
        
    except Exception as e:
        print(f"❌ NGA access failed: {e}")
        return False

async def test_login_page():
    """测试登录页面访问"""
    print_subsection("Testing Login Page")
    
    try:
        crawler = SeleniumNGACrawler(headless=True, manual_captcha=False)
        crawler.driver = crawler._setup_driver()
        
        # 访问登录页面
        login_url = "https://bbs.nga.cn/nuke.php?__lib=login&__act=login_page"
        crawler.driver.get(login_url)
        await asyncio.sleep(3)
        
        # 检查登录表单元素
        username_found = False
        password_found = False
        captcha_found = False
        
        username_selectors = [
            "input[name='username']",
            "input[name='uid']",
            "input[name='email']",
            "input[id='username']",
            "input[id='uid']"
        ]
        
        for selector in username_selectors:
            try:
                element = crawler.driver.find_element(crawler.driver.find_element.__self__.__class__.By.CSS_SELECTOR, selector)
                username_found = True
                print(f"   ✅ Username field found: {selector}")
                break
            except:
                continue
        
        password_selectors = [
            "input[name='password']",
            "input[name='passwd']",
            "input[id='password']",
            "input[type='password']"
        ]
        
        for selector in password_selectors:
            try:
                element = crawler.driver.find_element(crawler.driver.find_element.__self__.__class__.By.CSS_SELECTOR, selector)
                password_found = True
                print(f"   ✅ Password field found: {selector}")
                break
            except:
                continue
        
        # 检查验证码
        captcha_selectors = [
            "img[src*='captcha']",
            "img[src*='verify']",
            "img[src*='code']"
        ]
        
        for selector in captcha_selectors:
            try:
                element = crawler.driver.find_element(crawler.driver.find_element.__self__.__class__.By.CSS_SELECTOR, selector)
                captcha_found = True
                print(f"   ⚠️ Captcha found: {selector}")
                break
            except:
                continue
        
        if username_found and password_found:
            print(f"✅ Login form elements found")
            if captcha_found:
                print(f"   ⚠️ Captcha detected - manual solving required")
            else:
                print(f"   ✅ No captcha detected")
        else:
            print(f"❌ Login form incomplete")
            print(f"   Username field: {'✅' if username_found else '❌'}")
            print(f"   Password field: {'✅' if password_found else '❌'}")
        
        crawler.close()
        return username_found and password_found
        
    except Exception as e:
        print(f"❌ Login page test failed: {e}")
        return False

async def test_forum_crawling():
    """测试论坛内容爬取"""
    print_subsection("Testing Forum Crawling")
    
    try:
        crawler = SeleniumNGACrawler(headless=True, manual_captcha=False)
        crawler.driver = crawler._setup_driver()
        
        # 测试爬取论坛内容（无需登录）
        forum_url = "https://bbs.nga.cn/thread.php?fid=-7"  # 网事杂谈
        items = await crawler.crawl_with_selenium(forum_url)
        
        if items:
            print(f"✅ Forum crawling successful")
            print(f"   Found {len(items)} items")
            
            # 显示前3个项目
            for i, item in enumerate(items[:3], 1):
                print(f"   {i}. {item.title[:50]}...")
                print(f"      Author: {item.author or 'Unknown'}")
                print(f"      Comments: {item.comment_count or 'N/A'}")
        else:
            print(f"⚠️ No items found - may need login or different URL")
        
        crawler.close()
        return len(items) > 0 if items else False
        
    except Exception as e:
        print(f"❌ Forum crawling failed: {e}")
        return False

async def interactive_login_test():
    """交互式登录测试"""
    print_subsection("Interactive Login Test")
    
    print("\n⚠️ This test requires manual interaction")
    print("Do you want to test login with real credentials? (y/n): ", end="")
    
    try:
        choice = input().strip().lower()
        if choice != 'y':
            print("Skipping interactive login test")
            return True
    except:
        print("Skipping interactive login test")
        return True
    
    print("\nEnter your NGA credentials:")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    if not username or not password:
        print("❌ Username and password required")
        return False
    
    try:
        crawler = SeleniumNGACrawler(headless=False, manual_captcha=True)
        crawler.driver = crawler._setup_driver()
        
        print("\n🔄 Starting login process...")
        print("If captcha appears, solve it manually in the browser")
        
        success = await crawler.login_with_selenium(username, password)
        
        if success:
            print("✅ Login successful!")
            
            # 获取cookies
            cookies = crawler.get_cookies_dict()
            print(f"\n📋 Extracted cookies:")
            for key, value in cookies.items():
                print(f"   {key}: {value[:20]}...")
            
            # 测试爬取
            print("\n🔄 Testing crawling with login...")
            items = await crawler.crawl()
            
            if items:
                print(f"✅ Crawling successful - found {len(items)} items")
            else:
                print(f"⚠️ Crawling returned no items")
        else:
            print("❌ Login failed")
        
        crawler.close()
        return success
        
    except Exception as e:
        print(f"❌ Interactive login test failed: {e}")
        return False

async def main():
    """主测试函数"""
    print_separator("NGA Selenium Crawler Test Suite")
    
    print("\n🧪 Testing Selenium-based NGA crawler...")
    print("This crawler can handle login with captcha verification")
    
    tests = [
        ("Selenium Setup", test_selenium_setup),
        ("NGA Access", test_nga_access),
        ("Login Page", test_login_page),
        ("Forum Crawling", test_forum_crawling),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print_separator(f"Test: {test_name}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # 交互式登录测试（可选）
    print_separator("Optional: Interactive Login Test")
    try:
        login_result = await interactive_login_test()
        results.append(("Interactive Login", login_result))
    except Exception as e:
        print(f"❌ Interactive login test crashed: {e}")
        results.append(("Interactive Login", False))
    
    # 显示测试结果
    print_separator("Test Results Summary")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Selenium crawler is ready to use.")
    elif passed >= total - 1:
        print("\n✅ Most tests passed. Selenium crawler should work.")
    else:
        print("\n⚠️ Some tests failed. Check the issues above.")
    
    print("\n💡 Usage Tips:")
    print("   1. For production use, consider headless=True")
    print("   2. Manual captcha solving requires headless=False")
    print("   3. Save extracted cookies for future use")
    print("   4. Consider implementing OCR for automatic captcha solving")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Test suite crashed: {e}")
        import traceback
        traceback.print_exc()