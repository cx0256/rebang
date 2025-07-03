# 热榜数据爬虫系统使用指南

## 概述

本系统提供了完整的热榜数据爬取解决方案，支持NGA杂谈、知乎热榜等平台的数据获取，并通过API接口提供给前端使用。

## 系统架构

```
爬虫系统架构:
├── 爬虫模块 (app/crawlers/)
│   ├── base.py              # 基础爬虫类
│   ├── nga_crawler.py       # NGA杂谈爬虫
│   ├── zhihu_crawler.py     # 知乎热榜爬虫
│   └── crawler_manager.py   # 爬虫管理器
├── API接口 (app/api/v1/endpoints/)
│   ├── crawlers.py          # 爬虫管理API
│   └── hot_items.py         # 热榜数据API
├── 定时任务 (app/core/)
│   └── scheduler.py         # 任务调度器
└── 数据模型 (app/models/)
    ├── platform.py          # 平台模型
    ├── category.py          # 分类模型
    └── hot_item.py          # 热榜条目模型
```

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动服务

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 测试爬虫功能

```bash
cd backend
python test_crawlers.py
```

## API接口说明

### 爬虫管理接口

#### 1. 手动触发所有爬虫
```http
POST /api/v1/crawlers/crawl/all
```

#### 2. 手动触发单个爬虫
```http
POST /api/v1/crawlers/crawl/{crawler_name}
```

支持的爬虫名称:
- `nga_zatan`: NGA杂谈
- `zhihu_hot`: 知乎热榜

#### 3. 获取爬虫列表
```http
GET /api/v1/crawlers/crawlers
```

#### 4. 获取定时任务状态
```http
GET /api/v1/crawlers/jobs
```

#### 5. 暂停/恢复定时任务
```http
POST /api/v1/crawlers/jobs/{job_id}/pause
POST /api/v1/crawlers/jobs/{job_id}/resume
```

### 热榜数据接口

#### 1. 获取所有热榜数据
```http
GET /api/v1/hot
```

#### 2. 获取指定平台热榜
```http
GET /api/v1/hot/{platform_name}
```

#### 3. 获取指定分类热榜
```http
GET /api/v1/hot/{platform_name}/{category_name}
```

#### 4. 分页获取热榜条目
```http
GET /api/v1/hot-items/?page=1&size=20&platform_name=知乎&category_name=热榜
```

## 爬虫配置

### 定时任务配置

系统默认配置:
- 热榜爬取任务: 每30分钟执行一次
- 数据清理任务: 每天凌晨2点执行（删除7天前的数据）
- 缓存清理任务: 每小时执行一次

### 添加新的爬虫

1. 创建新的爬虫类，继承 `BaseCrawler`:

```python
from app.crawlers.base import BaseCrawler, HotItem

class NewSiteCrawler(BaseCrawler):
    def __init__(self):
        super().__init__("新站点", "热榜")
        self.base_url = "https://example.com"
    
    async def crawl(self) -> List[HotItem]:
        # 实现具体的爬取逻辑
        pass
```

2. 在爬虫管理器中注册:

```python
from app.crawlers.crawler_manager import crawler_manager
from .new_site_crawler import NewSiteCrawler

crawler_manager.register_crawler('new_site_hot', NewSiteCrawler)
```

## 前端集成

### 1. 获取热榜数据

```javascript
// 获取所有热榜数据
const response = await fetch('/api/v1/hot');
const data = await response.json();

// 获取知乎热榜
const zhihuResponse = await fetch('/api/v1/hot/知乎/热榜');
const zhihuData = await zhihuResponse.json();
```

### 2. 手动触发爬取

```javascript
// 触发所有爬虫
const crawlResponse = await fetch('/api/v1/crawlers/crawl/all', {
    method: 'POST'
});

// 触发知乎爬虫
const zhihuCrawlResponse = await fetch('/api/v1/crawlers/crawl/zhihu_hot', {
    method: 'POST'
});
```

### 3. 实时数据更新

建议在前端实现以下功能:
- 定时刷新数据（每5-10分钟）
- 显示数据更新时间
- 提供手动刷新按钮
- 加载状态指示器

## 数据结构

### HotItem 数据结构

```python
@dataclass
class HotItem:
    title: str              # 标题
    url: str               # 链接
    rank: int              # 排名
    hot_value: str         # 热度值（可选）
    author: str            # 作者（可选）
    comment_count: int     # 评论数（可选）
    publish_time: datetime # 发布时间（可选）
    summary: str           # 摘要（可选）
    tags: List[str]        # 标签（可选）
```

### API响应格式

```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "title": "热榜标题",
            "url": "https://example.com/article/123",
            "rank": 1,
            "hot_value": "100万热度",
            "author": "作者名",
            "comment_count": 1234,
            "platform_name": "知乎",
            "category_name": "热榜",
            "crawled_at": "2024-01-01T12:00:00Z"
        }
    ],
    "total": 50,
    "page": 1,
    "size": 20
}
```

## 注意事项

### 1. 反爬虫策略

- 设置合理的请求间隔
- 使用随机User-Agent
- 遵守robots.txt规则
- 避免频繁请求同一接口

### 2. 错误处理

- 网络超时处理
- 页面结构变化适配
- 数据库连接异常处理
- 日志记录和监控

### 3. 性能优化

- 使用Redis缓存热门数据
- 异步并发爬取
- 数据库连接池
- 定期清理旧数据

### 4. 法律合规

- 遵守网站服务条款
- 尊重版权和隐私
- 合理使用公开数据
- 不进行商业用途滥用

## 故障排除

### 常见问题

1. **爬虫无法获取数据**
   - 检查网络连接
   - 验证目标网站是否可访问
   - 查看日志错误信息
   - 检查页面结构是否变化

2. **定时任务不执行**
   - 检查调度器是否启动
   - 查看任务配置是否正确
   - 检查系统时间设置

3. **数据库连接失败**
   - 检查数据库服务状态
   - 验证连接配置
   - 检查网络连通性

### 日志查看

系统使用loguru进行日志记录，可以通过以下方式查看:

```bash
# 查看实时日志
tail -f logs/app.log

# 查看错误日志
grep "ERROR" logs/app.log
```

## 扩展开发

### 添加新平台支持

1. 分析目标网站结构
2. 创建对应的爬虫类
3. 实现数据解析逻辑
4. 注册到爬虫管理器
5. 测试和调试
6. 更新文档

### 自定义数据处理

可以在爬虫中添加自定义的数据处理逻辑:
- 内容过滤和清洗
- 关键词提取
- 情感分析
- 数据去重

## 联系支持

如有问题或建议，请通过以下方式联系:
- 提交GitHub Issue
- 发送邮件至开发团队
- 查看项目文档和Wiki