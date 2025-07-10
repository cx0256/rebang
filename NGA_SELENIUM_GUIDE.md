# NGA Selenium爬虫使用指南

## 概述

基于Selenium的NGA爬虫可以解决传统HTTP请求方式遇到的验证码和复杂登录问题。通过模拟真实浏览器操作，这个方案能够：

- ✅ 自动处理JavaScript渲染的页面
- ✅ 支持手动验证码输入
- ✅ 获取登录后的有效Cookie
- ✅ 模拟真实用户行为，降低被封风险
- ✅ 支持无头模式和可视化模式

## 环境要求

### 1. 安装依赖

```bash
# 安装Selenium
pip install selenium

# 如果需要其他依赖
pip install webdriver-manager  # 可选：自动管理ChromeDriver
```

### 2. 安装ChromeDriver

**方法一：手动下载**
1. 访问 [ChromeDriver下载页面](https://chromedriver.chromium.org/)
2. 下载与你的Chrome版本匹配的ChromeDriver
3. 将ChromeDriver添加到系统PATH中

**方法二：使用webdriver-manager（推荐）**
```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
```

### 3. 验证安装

运行测试脚本验证环境：
```bash
python test_selenium_nga.py
```

## 使用方法

### 1. 基本使用

```python
import asyncio
from backend.app.crawlers.nga_selenium_crawler import SeleniumNGACrawler

async def basic_usage():
    # 创建爬虫实例
    crawler = SeleniumNGACrawler(
        headless=True,      # 无头模式，设为False可看到浏览器
        manual_captcha=True # 手动处理验证码
    )
    
    try:
        # 初始化浏览器
        crawler.driver = crawler._setup_driver()
        
        # 爬取内容（无需登录）
        items = await crawler.crawl()
        
        print(f"爬取到 {len(items)} 条内容")
        for item in items[:5]:
            print(f"- {item.title}")
    
    finally:
        crawler.close()

# 运行
asyncio.run(basic_usage())
```

### 2. 带登录的使用

```python
async def login_usage():
    # 使用可视化模式进行登录（便于处理验证码）
    crawler = SeleniumNGACrawler(
        headless=False,     # 显示浏览器窗口
        manual_captcha=True # 手动处理验证码
    )
    
    try:
        # 初始化浏览器
        crawler.driver = crawler._setup_driver()
        
        # 登录
        success = await crawler.login_with_selenium(
            username="your_username",
            password="your_password"
        )
        
        if success:
            print("登录成功！")
            
            # 获取Cookie
            cookies = crawler.get_cookies_dict()
            print(f"获取到的Cookie: {cookies}")
            
            # 保存Cookie供后续使用
            import json
            with open('nga_cookies.json', 'w') as f:
                json.dump(cookies, f)
            
            # 爬取内容
            items = await crawler.crawl()
            print(f"爬取到 {len(items)} 条内容")
        else:
            print("登录失败")
    
    finally:
        crawler.close()

asyncio.run(login_usage())
```

### 3. 验证码处理

当遇到验证码时，有两种处理方式：

**手动处理（推荐）：**
```python
crawler = SeleniumNGACrawler(
    headless=False,     # 必须显示浏览器
    manual_captcha=True
)

# 登录时会自动暂停，等待用户手动输入验证码
```

**自动处理（需要额外开发）：**
```python
# 可以集成OCR服务来自动识别验证码
# 例如：百度OCR、腾讯OCR、或开源OCR库
```

## 集成到现有工具

### 1. 更新nga_unified_tool.py

在统一工具中添加Selenium选项：

```python
# 在nga_unified_tool.py中添加
def show_selenium_menu():
    print("\n🤖 Selenium爬虫选项:")
    print("1. 测试Selenium环境")
    print("2. 使用Selenium登录获取Cookie")
    print("3. 使用Selenium爬取内容")
    print("4. 返回主菜单")

async def handle_selenium_login():
    """使用Selenium进行登录"""
    try:
        from backend.app.crawlers.nga_selenium_crawler import SeleniumNGACrawler
    except ImportError:
        print("❌ Selenium未安装，请运行: pip install selenium")
        return
    
    username = input("请输入用户名: ").strip()
    password = input("请输入密码: ").strip()
    
    if not username or not password:
        print("❌ 用户名和密码不能为空")
        return
    
    crawler = SeleniumNGACrawler(headless=False, manual_captcha=True)
    
    try:
        crawler.driver = crawler._setup_driver()
        print("\n🔄 开始登录过程...")
        print("如果出现验证码，请在浏览器中手动输入")
        
        success = await crawler.login_with_selenium(username, password)
        
        if success:
            print("✅ 登录成功！")
            cookies = crawler.get_cookies_dict()
            
            # 保存Cookie
            save_cookies_to_config(cookies)
            print("✅ Cookie已保存到配置文件")
        else:
            print("❌ 登录失败")
    
    finally:
        crawler.close()
```

### 2. 更新nga_quick_start.py

添加Selenium快速选项：

```python
# 在nga_quick_start.py中添加
def show_quick_menu():
    print("\n🚀 NGA快速启动工具")
    print("1. 检查Cookie状态")
    print("2. 设置Cookie (手动)")
    print("3. 设置Cookie (Selenium登录)"  # 新增
    print("4. 测试爬虫")
    print("5. 一键测试")
    print("6. 帮助")
    print("0. 退出")
```

## 配置选项

### SeleniumNGACrawler参数

```python
crawler = SeleniumNGACrawler(
    headless=True,          # 是否无头模式
    manual_captcha=True     # 是否手动处理验证码
)
```

### Chrome选项自定义

```python
def _setup_driver(self):
    options = Options()
    
    # 基本选项
    if self.headless:
        options.add_argument('--headless')
    
    # 性能优化
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    # 反检测
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 自定义User-Agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    return webdriver.Chrome(options=options)
```

## 最佳实践

### 1. 性能优化

```python
# 禁用图片加载
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)

# 禁用CSS
options.add_argument('--disable-extensions')
options.add_argument('--disable-plugins')
```

### 2. 错误处理

```python
try:
    crawler = SeleniumNGACrawler()
    crawler.driver = crawler._setup_driver()
    # 使用爬虫
except Exception as e:
    print(f"错误: {e}")
finally:
    if crawler:
        crawler.close()
```

### 3. Cookie管理

```python
# 保存Cookie
cookies = crawler.get_cookies_dict()
with open('nga_cookies.json', 'w') as f:
    json.dump(cookies, f)

# 加载Cookie到其他爬虫
with open('nga_cookies.json', 'r') as f:
    cookies = json.load(f)
    # 使用cookies进行HTTP请求
```

## 故障排除

### 1. ChromeDriver问题

**错误：** `selenium.common.exceptions.WebDriverException: 'chromedriver' executable needs to be in PATH`

**解决：**
- 下载ChromeDriver并添加到PATH
- 或使用webdriver-manager自动管理

### 2. Chrome版本不匹配

**错误：** `This version of ChromeDriver only supports Chrome version XX`

**解决：**
- 更新Chrome浏览器
- 或下载匹配版本的ChromeDriver

### 3. 验证码问题

**问题：** 无法处理验证码

**解决：**
- 使用`headless=False`显示浏览器
- 设置`manual_captcha=True`手动输入
- 考虑集成OCR服务

### 4. 登录失败

**问题：** 登录后没有获取到有效Cookie

**解决：**
- 检查用户名密码是否正确
- 确认验证码输入正确
- 检查NGA网站是否有变化

## 与传统方案对比

| 特性 | HTTP请求 | Selenium |
|------|----------|----------|
| 速度 | 快 | 较慢 |
| 资源消耗 | 低 | 高 |
| 验证码处理 | 困难 | 容易 |
| JavaScript支持 | 无 | 完整 |
| 反爬虫能力 | 弱 | 强 |
| 维护成本 | 高 | 低 |

## 推荐使用场景

1. **首次获取Cookie** - 使用Selenium登录获取有效Cookie
2. **验证码频繁** - 当HTTP方式经常遇到验证码时
3. **页面复杂** - 当页面大量使用JavaScript时
4. **开发调试** - 可视化调试爬虫逻辑

## 后续优化建议

1. **集成OCR服务** - 自动识别验证码
2. **代理支持** - 添加代理池支持
3. **Cookie池** - 维护多个有效Cookie
4. **智能切换** - 根据情况自动选择HTTP或Selenium
5. **分布式支持** - 支持多实例并行爬取

## 总结

Selenium方案虽然资源消耗较大，但能有效解决NGA登录和验证码问题。建议的使用策略：

1. 使用Selenium获取初始Cookie
2. 日常爬取使用HTTP请求+Cookie
3. 当Cookie失效时，再次使用Selenium更新

这样既保证了成功率，又控制了资源消耗。