from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基本信息
    APP_NAME: str = "热榜API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "lo"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/momoyu"
    DATABASE_ECHO: bool = False  # 是否打印SQL语句
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8080",
        "http://127.0.0.1:8080"
    ]
    
    # 爬虫配置
    CRAWLER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    CRAWLER_DELAY: float = 1.0  # 爬取延迟（秒）
    CRAWLER_TIMEOUT: int = 30   # 请求超时（秒）
    CRAWLER_RETRY_TIMES: int = 3  # 重试次数
    
    # 缓存配置
    CACHE_EXPIRE_TIME: int = 300  # 缓存过期时间（秒）
    HOT_LIST_CACHE_TIME: int = 600  # 热榜缓存时间（秒）
    
    # 定时任务配置
    SCHEDULER_TIMEZONE: str = "Asia/Shanghai"
    CRAWL_INTERVAL_MINUTES: int = 30  # 爬取间隔（分钟）
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    LOG_ROTATION: str = "1 day"
    LOG_RETENTION: str = "30 days"
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # API限流配置
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # 外部API配置
    ZHIHU_API_BASE: str = "https://www.zhihu.com/api/v4"
    WEIBO_API_BASE: str = "https://weibo.com/ajax"
    GITHUB_API_BASE: str = "https://api.github.com"
    BILIBILI_API_BASE: str = "https://api.bilibili.com"
    
    # 代理配置（可选）
    HTTP_PROXY: Optional[str] = None
    HTTPS_PROXY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 确保日志目录存在
        log_dir = Path(self.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 确保上传目录存在
        upload_dir = Path(self.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)


# 创建全局配置实例
settings = Settings()


# 开发环境配置
class DevelopmentSettings(Settings):
    DEBUG: bool = True
    DATABASE_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"


# 生产环境配置
class ProductionSettings(Settings):
    DEBUG: bool = False
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")


# 测试环境配置
class TestingSettings(Settings):
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/momoyu_test"
    REDIS_DB: int = 1


def get_settings() -> Settings:
    """根据环境变量获取配置"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()