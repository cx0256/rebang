from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from loguru import logger
from datetime import datetime
from typing import Callable, Optional

from app.core.config import settings


class SchedulerManager:
    """定时任务调度器管理器"""
    
    def __init__(self):
        # 配置调度器
        jobstores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': AsyncIOExecutor()
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 30
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=settings.SCHEDULER_TIMEZONE
        )
        
        self.is_running = False
    
    def start(self) -> None:
        """启动调度器"""
        if not self.is_running:
            try:
                self.scheduler.start()
                self.is_running = True
                logger.info("Scheduler started successfully")
                
                # 添加默认的爬取任务
                self._add_default_jobs()
                
            except Exception as e:
                logger.error(f"Failed to start scheduler: {e}")
                raise
    
    def shutdown(self, wait: bool = True) -> None:
        """关闭调度器"""
        if self.is_running:
            try:
                self.scheduler.shutdown(wait=wait)
                self.is_running = False
                logger.info("Scheduler shutdown successfully")
            except Exception as e:
                logger.error(f"Error shutting down scheduler: {e}")
    
    def add_interval_job(
        self,
        func: Callable,
        minutes: int,
        job_id: str,
        args: tuple = None,
        kwargs: dict = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> None:
        """添加间隔执行任务"""
        try:
            self.scheduler.add_job(
                func=func,
                trigger=IntervalTrigger(minutes=minutes),
                id=job_id,
                args=args or (),
                kwargs=kwargs or {},
                start_date=start_date,
                end_date=end_date,
                replace_existing=True
            )
            logger.info(f"Added interval job: {job_id} (every {minutes} minutes)")
        except Exception as e:
            logger.error(f"Failed to add interval job {job_id}: {e}")
    
    def add_cron_job(
        self,
        func: Callable,
        cron_expression: str,
        job_id: str,
        args: tuple = None,
        kwargs: dict = None
    ) -> None:
        """添加Cron表达式任务"""
        try:
            # 解析cron表达式
            cron_parts = cron_expression.split()
            if len(cron_parts) != 5:
                raise ValueError("Invalid cron expression")
            
            minute, hour, day, month, day_of_week = cron_parts
            
            self.scheduler.add_job(
                func=func,
                trigger=CronTrigger(
                    minute=minute,
                    hour=hour,
                    day=day,
                    month=month,
                    day_of_week=day_of_week
                ),
                id=job_id,
                args=args or (),
                kwargs=kwargs or {},
                replace_existing=True
            )
            logger.info(f"Added cron job: {job_id} ({cron_expression})")
        except Exception as e:
            logger.error(f"Failed to add cron job {job_id}: {e}")
    
    def remove_job(self, job_id: str) -> bool:
        """移除任务"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")
            return False
    
    def pause_job(self, job_id: str) -> bool:
        """暂停任务"""
        try:
            self.scheduler.pause_job(job_id)
            logger.info(f"Paused job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {e}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """恢复任务"""
        try:
            self.scheduler.resume_job(job_id)
            logger.info(f"Resumed job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {e}")
            return False
    
    def get_jobs(self) -> list:
        """获取所有任务"""
        try:
            jobs = self.scheduler.get_jobs()
            return [
                {
                    'id': job.id,
                    'name': job.name,
                    'func': str(job.func),
                    'trigger': str(job.trigger),
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in jobs
            ]
        except Exception as e:
            logger.error(f"Failed to get jobs: {e}")
            return []
    
    def _add_default_jobs(self) -> None:
        """添加默认的定时任务"""
        from app.crawlers.crawler_manager import crawler_manager
        
        # 添加热榜爬取任务（每30分钟执行一次）
        self.add_interval_job(
            func=crawler_manager.run_crawl_task,
            minutes=30,
            job_id="crawl_hot_lists"
        )
        
        # 添加数据清理任务（每天凌晨2点执行）
        self.add_cron_job(
            func=self._cleanup_old_data,
            cron_expression="0 2 * * *",
            job_id="cleanup_old_data"
        )
        
        # 添加缓存清理任务（每小时执行）
        self.add_cron_job(
            func=self._cleanup_cache,
            cron_expression="0 * * * *",
            job_id="cleanup_cache"
        )
        
        logger.info("Default scheduled jobs added")
    
    async def _cleanup_cache(self) -> None:
        """清理过期缓存"""
        try:
            from app.core.redis import redis_manager
            
            # 获取所有缓存键
            keys = await redis_manager.keys("cache:*")
            expired_count = 0
            
            for key in keys:
                ttl = await redis_manager.ttl(key)
                if ttl == -1:  # 没有过期时间的键
                    await redis_manager.expire(key, settings.CACHE_EXPIRE_TIME)
                elif ttl == -2:  # 已过期的键
                    await redis_manager.delete(key)
                    expired_count += 1
            
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired cache keys")
                
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
    
    async def _cleanup_old_data(self) -> None:
        """清理旧数据"""
        try:
            from app.core.database import get_db
            from app.models.hot_item import HotItem
            from sqlalchemy import delete
            from datetime import datetime, timedelta
            
            async for db in get_db():
                try:
                    # 删除7天前的数据
                    cutoff_date = datetime.now() - timedelta(days=7)
                    stmt = delete(HotItem).where(HotItem.crawled_at < cutoff_date)
                    result = await db.execute(stmt)
                    await db.commit()
                    
                    deleted_count = result.rowcount
                    if deleted_count > 0:
                        logger.info(f"Cleaned up {deleted_count} old hot items")
                    
                except Exception as e:
                    logger.error(f"Database cleanup error: {e}")
                    await db.rollback()
                finally:
                    break
                    
        except Exception as e:
            logger.error(f"Old data cleanup error: {e}")


# 创建全局调度器实例
scheduler = SchedulerManager()