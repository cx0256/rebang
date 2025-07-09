import asyncio
from app.core.database import engine, Base
from loguru import logger

async def init_database():
    """初始化数据库"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
        print("数据库初始化成功")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        print(f"数据库初始化失败: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_database())