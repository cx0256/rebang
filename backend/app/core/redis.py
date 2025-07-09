import redis.asyncio as redis
from typing import Optional, Any, Union
import json
from loguru import logger
from datetime import timedelta

from app.core.config import settings


class RedisManager:
    """Redis缓存管理器"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.connected = False
    
    async def connect(self) -> None:
        """连接Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # 测试连接
            await self.redis_client.ping()
            self.connected = True
            logger.info("Redis connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.connected = False
            raise
    
    async def disconnect(self) -> None:
        """断开Redis连接"""
        if self.redis_client:
            await self.redis_client.close()
            self.connected = False
            logger.info("Redis disconnected")
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[Union[int, timedelta]] = None
    ) -> bool:
        """设置缓存"""
        if not self.connected or not self.redis_client:
            logger.warning("Redis not connected, skipping cache set")
            return False
        
        try:
            # 序列化值
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            elif not isinstance(value, str):
                value = str(value)
            
            # 设置过期时间
            if expire is None:
                expire = settings.CACHE_EXPIRE_TIME
            
            await self.redis_client.set(key, value, ex=expire)
            return True
            
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self.connected or not self.redis_client:
            logger.warning("Redis not connected, skipping cache get")
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value is None:
                return None
            
            # 尝试反序列化JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.connected or not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.connected or not self.redis_client:
            return False
        
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """设置键的过期时间"""
        if not self.connected or not self.redis_client:
            return False
        
        try:
            return await self.redis_client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis expire error: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """获取键的剩余生存时间"""
        if not self.connected or not self.redis_client:
            return -1
        
        try:
            return await self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Redis ttl error: {e}")
            return -1
    
    async def keys(self, pattern: str = "*") -> list:
        """获取匹配模式的所有键"""
        if not self.connected or not self.redis_client:
            return []
        
        try:
            return await self.redis_client.keys(pattern)
        except Exception as e:
            logger.error(f"Redis keys error: {e}")
            return []
    
    async def flushdb(self) -> bool:
        """清空当前数据库"""
        if not self.connected or not self.redis_client:
            return False
        
        try:
            await self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis flushdb error: {e}")
            return False
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.redis_client:
                return False
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """递增计数器"""
        if not self.connected or not self.redis_client:
            return 0
        
        try:
            return await self.redis_client.incr(key, amount)
        except Exception as e:
            logger.error(f"Redis incr error: {e}")
            return 0
    
    async def decr(self, key: str, amount: int = 1) -> int:
        """递减计数器"""
        if not self.connected or not self.redis_client:
            return 0
        
        try:
            return await self.redis_client.decr(key, amount)
        except Exception as e:
            logger.error(f"Redis decr error: {e}")
            return 0

    async def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的所有键"""
        if not self.connected or not self.redis_client:
            return 0
        
        try:
            keys_to_delete = await self.keys(pattern)
            if not keys_to_delete:
                return 0
            
            deleted_count = await self.redis_client.delete(*keys_to_delete)
            return deleted_count
        except Exception as e:
            logger.error(f"Redis delete_pattern error: {e}")
            return 0

# 全局Redis管理器实例
redis_manager = RedisManager()


# 缓存装饰器
def cache_result(key_prefix: str, expire: int = None):
    """缓存结果装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached_result = await redis_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await redis_manager.set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator