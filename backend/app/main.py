from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from loguru import logger

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.core.scheduler import scheduler
from app.crawlers.crawler_manager import crawler_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    try:
        # 启动时执行
        logger.info("Starting MoMoYu API Server...")
        
        # 创建数据库表
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # 启动定时任务调度器
        scheduler.start()
        logger.info("Scheduler started")

        # 立即执行一次爬虫任务
        try:
            import asyncio
            await asyncio.sleep(5)  # 等待5秒，确保数据库准备就绪
            await crawler_manager.run_crawl_task()
            logger.info("Initial crawl task executed successfully")
        except Exception as e:
            logger.error(f"Error during initial crawl task: {e}")
        
        yield
    
    except Exception as e:
        logger.error(f"Error during application lifespan: {e}")
    finally:
        # 关闭时执行
        logger.info("Shutting down MoMoYu API Server...")
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Scheduler stopped")


# 创建FastAPI应用实例
app = FastAPI(
    title="热榜 API",
    description="聚合各大平台热榜数据的API服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用热榜API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "message": "API服务运行正常"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理器"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理器"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "服务器内部错误",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="info"
    )